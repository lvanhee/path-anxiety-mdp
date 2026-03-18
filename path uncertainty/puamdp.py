from collections import Counter
from math import log


class PUAMDP:
    def __init__(self, rewards, actions, transitions, scale_vals=[]):
        self.states = [x for x in list(rewards.keys()) if x not in list(actions)] + list(actions.keys())
        self.rewards = rewards
        self.actions = actions
        self.transitions = transitions
        self.scale_values = scale_vals

    def compute_optimal_policy(self, w, h, s0):
        """
        Computes the optimal policy for a PUA-MDP by first determining max and min values for reward and uncertainty
        optimality and then incorporating the weight
        :param w: the weight of importance for avoiding cpue
        :param h: the maximum horizon
        :param s0: the starting state
        :return: the optimal policy, expected reward and expected cpue
        """
        if w == 0 or w == 1:
            return self.optimal_policy(w, h, determine_scale=True)
        if not self.scale_values:
            _, max_rew, max_unc = self.optimal_policy(0, h, determine_scale=True)
            _, min_rew, min_unc = self.optimal_policy(1, h, determine_scale=True)
            self.scale_values = [max_rew[s0], min_rew[s0], max_unc[s0], min_unc[s0]]
        return self.optimal_policy(w, h, determine_scale=False)

    def optimal_policy(self, w, h, determine_scale=False):
        """
        Gets the optimal policy
        :param w: the weight of importance for avoiding path uncertainty
        :param h: the maximum horizon
        :param determine_scale: whether the scales still need to be determined
        :return: the optimal policy, expected reward and expected path uncertainty
        """

        # Initialize dictionaries with horizon 0
        policy = {}
        value = {0: {}}
        cpue = {0: {}}
        instant_unc = {0: {}}
        policy_transitions = {0: {}}
        prob_counts = {0: {}}

        for state in self.states:
            value[0][state] = self.rewards[state]
            cpue[0][state] = 0
            instant_unc[0][state] = 0
            policy_transitions[0][state] = [1]
            prob_counts[0][state] = Counter(policy_transitions[0][state])

        for i in range(1, h + 1):
            print(i, '/', h)
            policy[i] = {}
            policy_transitions[i] = {}
            prob_counts[i] = {}
            value[i] = {}
            cpue[i] = {}
            instant_unc[i] = {}
            for s in self.states:
                if s in self.actions:  # If s is not a terminal state, compute the policy
                    policy[i][s] = self.get_policy(value, instant_unc, cpue, i, s, w, policy,
                                                   policy_transitions, prob_counts, determine_scale)
                instant_unc[i][s], policy_transitions, prob_counts = self.instant_uncertainty(policy, i, s,
                                                                                              policy_transitions,
                                                                                              prob_counts)
                value[i][s] = self.get_value(policy, value, i, s)
                cpue[i][s] = self.get_cpue(policy, cpue, i, s,
                                           instant_unc[i][s])
        for s in self.states:
            if s not in self.actions:
                del value[h][s]
                del cpue[h][s]
        return policy[h], value[h], cpue[h]

    def get_policy(self, value, instant_unc, cpue, i, s, w, policy, policy_transitions, prob_counts,
                   determine_scale):
        """
        Get the policy (optimal action) for a state-horizon combination
        :param value: dictionary to keep track of values
        :param instant_unc: dictionary to keep track of instant uncertainty
        :param cpue: dictionary to keep track of cumulative uncertainty
        :param i: the current horizon
        :param s: the current state
        :param w: the weight of importance for avoiding path uncertainty
        :param policy: dictionary to store policies
        :param policy_transitions: the probabilities for paths for a policy
        :param prob_counts: the counter for policy_transitions
        :param determine_scale: whether the scales still need to be determined
        :return: the optimal action
        """
        # start_t = time.time()
        action_scores = {}
        for action in self.actions[s]:

            # Temporary values
            policy[i][s] = action
            instant_unc[i][s], _, _ = self.instant_uncertainty(policy, i, s, policy_transitions, prob_counts,
                                                               test_actions=True)

            reward_factor = 0
            cpue_factor = 0
            for s_next, s_prob in [x for x in self.transitions[(s, action)]]:
                reward_factor += s_prob * value[i - 1][s_next]
                cpue_factor += s_prob * cpue[i - 1][s_next]
            pu_factor = instant_unc[i][s] + cpue_factor
            if determine_scale:
                action_scores[action] = (1 - w) * -1 * reward_factor + w * pu_factor
            else:
                normalized_reward = normalize(reward_factor, self.scale_values[1], self.scale_values[0])
                normalized_pu = normalize(pu_factor, self.scale_values[3], self.scale_values[2])
                action_scores[action] = (1 - w) * (1 - normalized_reward) + w * normalized_pu

        # Choose action with best score
        return min(action_scores, key=action_scores.get)

    def get_value(self, policy, value, i, s):
        """
        Get the value for a state-horizon combination
        :param policy: dictionary to store policies
        :param value: dictionary to keep track of values
        :param i: the current horizon
        :param s: the current state
        :return: the value of the state-horizon combination
        """
        # If terminal state, return the state reward
        if s not in self.actions:
            return self.rewards[s]
        next_state_value = 0
        for s_next, s_prob in [x for x in self.transitions[(s, policy[i][s])]]:
            next_state_value += s_prob * value[i - 1][s_next]
        return next_state_value + self.rewards[s]

    def get_cpue(self, policy, uncertainty_value, i, s, instant_uncertainty):
        """
        Get the cpue for a state-horizon-policy combination
        :param policy: dictionary to store policies
        :param uncertainty_value: the cumulative uncertainty of further states
        :param i: the current horizon
        :param s: the current state
        :param instant_uncertainty: dictionary to keep track of instant uncertainty
        :return: the cpue for a state-horizon-policy combination
        """
        # If terminal state, uncertainty is 0
        if s not in self.actions:
            return 0
        cpue = 0
        for s_next, s_prob in [x for x in self.transitions[(s, policy[i][s])]]:
            cpue += s_prob * uncertainty_value[i - 1][s_next]
        return cpue + instant_uncertainty

    def instant_uncertainty(self, policy, horizon, s, policy_transitions, prob_counts, test_actions=False):
        """
        Get the instant uncertainty for a state-horizon-policy combination
        :param policy: dictionary to store policies
        :param horizon: the current horizon
        :param s: the current state
        :param policy_transitions: the probabilities for paths for a policy
        :param prob_counts: the counter for policy_transitions
        :param test_actions: whether the policies are being tested
        :return: the instant uncertainty for a state-horizon-policy combination
        """
        if s not in self.actions:
            return 0, policy_transitions, prob_counts

        counts = Counter()
        for path_state, path_prob in self.transitions[(s, policy[horizon][s])]:
            if path_state not in self.actions:
                policy_transitions[horizon - 1][path_state] = [1]
                prob_counts[horizon - 1][path_state] = Counter(policy_transitions[horizon - 1][path_state])
            # Get probabilities for each possible path
            new_paths = []
            for i in policy_transitions[horizon-1][path_state]:
                new_path_prob = path_prob * i
                new_paths.append(new_path_prob)
                counts[new_path_prob] = prob_counts[horizon-1][path_state][i]

            policy_transitions[horizon][s] = append_dict_list(policy_transitions[horizon], s, new_paths)

        prob_counts[horizon][s] = counts
        policy_transitions[horizon][s] = set(policy_transitions[horizon][s])
        k = 100
        if len(policy_transitions[horizon][s]) > k:
            policy_transitions[horizon][s], prob_counts[horizon][s] = stay_within_bounds(policy_transitions[horizon][s],
                                                                                         prob_counts[horizon][s], k)
        # Compute entropy based on probabilities
        instant_uncertainty = get_entropy(prob_counts[horizon][s])
        if test_actions:
            del policy_transitions[horizon][s]
        return instant_uncertainty, policy_transitions, prob_counts


def append_dict_list(dictionary, key, value):
    """
    Appends to a list value in a dictionary or adds a list if it does not exist yet
    :param dictionary: the dictionary
    :param key: the key to add the value to
    :param value: the value to add
    :return: the new value for the key
    """
    if key in dictionary.keys():
        new_val = dictionary[key] + value
        return new_val
    else:
        return value


def normalize(value, min_val, max_val):
    """
    Normalizes a value
    :param value: the value to normalize
    :param min_val: the min value
    :param max_val: the max value
    :return: the normalized value
    """
    if max_val - min_val == 0:
        return 0
    return (value - min_val) / (max_val - min_val)


def stay_within_bounds(probability_list, prob_counts, k):
    """
    Get the probability distribution back to k items
    :param probability_list: list of probabilities
    :param prob_counts: the counter for probability_list
    :param k: the number to reduce the list to
    :return: the k-bounded probability list
    """
    to_remove = len(probability_list) - k
    for i in range(to_remove):
        probability_list = sorted(probability_list)
        closest_values = min([[a, b] for a, b in zip(probability_list, probability_list[1:])],
                             key=lambda x: x[1] - x[0])
        new_avg = (closest_values[0] * prob_counts[closest_values[0]] + closest_values[1] * prob_counts[
            closest_values[1]]) / (prob_counts[closest_values[0]] + prob_counts[closest_values[1]])
        probability_list.remove(closest_values[0])
        probability_list.remove(closest_values[1])
        probability_list.append(new_avg)
        prob_counts[new_avg] = prob_counts[closest_values[0]] + prob_counts[closest_values[1]]
        if new_avg != closest_values[0]:
            del prob_counts[closest_values[0]]
        if new_avg != closest_values[1]:
            del prob_counts[closest_values[1]]
    return probability_list, prob_counts


def get_entropy(prob_counts):
    """
    Get the entropy
    :param prob_counts: the probability distribution
    :return: the entropy
    """
    logs = []
    for path in prob_counts:
        logs.append(path*log(path, 2)*prob_counts[path])
    return -sum(logs)
