import csv
import time
from collections import defaultdict, Counter
from itertools import combinations

#Here I am Loading transactions from a CSV file into a list of sets
def load_transactions(file_name):
    transactions = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            transactions.append(set(row))
    return transactions

#Here generating frequent 1-itemsets (individual items with support >= min_support)
def get_frequent_1_itemsets(transactions, min_support):
    item_counts = Counter()
    for transaction in transactions:
        for item in transaction:
            item_counts[frozenset([item])] += 1
    return {itemset: count for itemset, count in item_counts.items() if count >= min_support}

#Generating candidate itemsets of size k from previous frequent itemsets
def apriori_gen(itemsets, k):
    candidates = set()
    itemsets = list(itemsets)
    for i in range(len(itemsets)):
        for j in range(i + 1, len(itemsets)):
            union_set = itemsets[i] | itemsets[j]
            if len(union_set) == k and not has_infrequent_subset(union_set, itemsets):
                candidates.add(union_set)
    return candidates

#Checking if a candidate itemset has any infrequent subset
def has_infrequent_subset(candidate, frequent_itemsets):
    for subset in combinations(candidate, len(candidate) - 1):
        if frozenset(subset) not in frequent_itemsets:
            return True
    return False

#Filtering candidates based on their support in the transactions
def filter_candidates(transactions, candidates, min_support):
    item_counts = defaultdict(int)
    for transaction in transactions:
        for candidate in candidates:
            if candidate.issubset(transaction):
                item_counts[candidate] += 1
    return {itemset: count for itemset, count in item_counts.items() if count >= min_support}

#This is Main Apriori algorithm to find frequent itemsets
def apriori(transactions, min_support):
    frequent_itemsets = []
    current_itemsets = get_frequent_1_itemsets(transactions, min_support)
    k = 2
    while current_itemsets:
        frequent_itemsets.extend(current_itemsets.keys())
        candidates = apriori_gen(current_itemsets.keys(), k)
        current_itemsets = filter_candidates(transactions, candidates, min_support)
        k += 1
    return [set(itemset) for itemset in frequent_itemsets]

#Getting maximal frequent itemsets (largest itemsets that are not a subset of any other frequent itemset)
def get_maximal_frequent_itemsets(frequent_itemsets):
    maximal = []
    for itemset in sorted(frequent_itemsets, key=len, reverse=True):
        if not any(set(itemset).issubset(set(max_itemset)) for max_itemset in maximal):
            maximal.append(itemset)
    return maximal

#Running the Apriori algorithm, returning formatted output, total itemsets, and elapsed time
def run_apriori_algorithm(file_path, min_support):

    #Executeing the Apriori algorithm and formats the output for the Flask app.

    transactions = load_transactions(file_path)  #Loading transactions from the CSV files

    #Start timing
    start_time = time.time()

    #Running the Apriori algorithm
    frequent_itemsets = apriori(transactions, min_support)
    maximal_itemsets = get_maximal_frequent_itemsets(frequent_itemsets)

    #End timing
    end_time = time.time()
    elapsed_time = end_time - start_time

    #Desired formatting the output
    formatted_output = "{ " + " ".join(
        "{" + ", ".join(sorted(itemset)) + "}" for itemset in maximal_itemsets
    ) + " }"

    return formatted_output, len(maximal_itemsets), elapsed_time

#This is Main function to run the algorithm via command-line arguments
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Apriori Algorithm Implementation')
    parser.add_argument('-i', '--input', required=True, help='Input CSV file')
    parser.add_argument('-m', '--min_support', type=int, required=True, help='Minimum support value')
    args = parser.parse_args()

    #Running the algorithm and print results
    output, total_itemsets, elapsed_time = run_apriori_algorithm(args.input, args.min_support)
    print(f"Input file: {args.input}")
    print(f"Min_sup {args.min_support}")
    print(output)
    print(f"End - total items: {total_itemsets}")
    print(f"Elapsed Time: {elapsed_time} seconds")
