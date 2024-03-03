from bs4 import BeautifulSoup
import requests
import os
import os.path

"""
    NOTES:

"""

# URL of the webpage to scrape
url = "https://www.ifelsemedia.com/swordandglory/perklist/"
file_path = r"C:\Users\benjb\Downloads\Webscrape.txt"
class_list = [
    "cat_Occupation",   
    "cat_CombatSkill",
    "cat_Religion",
    "cat_Adventure",
    "cat_Clan",
    "cat_Personality",
]

trait_dict = {
    # Defence traits
    "health": [],
    "defense": [],
    "defense recovery"  : [],

    # Attacking traits 
    "dominance": [],
    "damage": [],
    "speed": [],
    "stamina": [],
    "stamina recovery": [],

    # Other
    "wealth": [],
    "glory": [],
    }

priority_list = ["dominance","damage","stamina","defense","stamina recovery","defense recovery","wealth","speed","health","glory",]

class TreeNode:
    def __init__(self, name, req, trait, score=0, depth=0):
        self.children = []
        self.name = name
        self.req = req
        self.trait = trait
        self.score = score
        self.num = 0        #optional
        self.depth = depth
        self.type = None

    def copy_childless(self):
        return TreeNode(self.name, self.req, self.trait, self.score)
    
    def add_child(self,new_child):
        self.children.append(new_child)

    # Given the name of the child, finds and removes the child from the list
    def remove_child(self,child_name):
        for c in self.children:
            if c.name == child_name:
                self.children.remove(c)
                print("Removed", c.name, "from", self.name)
                return
        

###############################################################################################
#                                   TREE FUNCTIONS
###############################################################################################
def find_name(root, target_name):
    if root is None:
        return None
    if target_name == root.name:
        return root
    # Recursively search in the children of the current node
    for child in root.children:
        result = find_name(child, target_name)
        if result:
            return result
    return None

# Assumes all required nodes are contained in the list
# Will recursively go forever if exception
def add_node(root, new_node, list=None):  
    # Adds class_name to root node 
    if new_node.req is None:
        root.children.append(new_node)
        new_node.type = new_node.name
        # print(f"    {root.name} -> {new_node.name}")
        return True
    
    # For level 1 skills
    elif len(new_node.req) <= 1:
        root.children.append(new_node)
        new_node.type = root.type
        # print(f"    {root.name} -> {new_node.name}")
        return True

    parent_node = find_name(root, new_node.req[1])

    if parent_node:
        # print(f"    {parent_node.name} -> {new_node.name}")
        parent_node.children.append(new_node)
        new_node.type = parent_node.type
        return True
    else:
        # print(f" x  \"{new_node.req[1]}\" not found.")
        if list:
            list.append(node)  
        else:
            print(f" x  \"{new_node.req[1]}\" not found.")

# get size from trait list
def count_nodes(root):
    if root is None:
        return 0
    
    # Initialize the count with 1 for the current node
    count = 1
    
    # Recursively count nodes in each child
    for child in root.children:
        count += count_nodes(child)
    
    return count

def assign_num(root):
    """Assigns num and depth to all nodes in a tree"""
    if root is None:
        return 0

    queue = []
    queue.append(root)
    count = 0 
    depth = 0

    while queue:
        level_size = len(queue)
        depth += 1 
        
        for _ in range(level_size):
            node = queue.pop(0)
            node.num = count
            node.depth = depth
            count += 1
            
            for child in node.children:
                queue.append(child)

    return count


# gives score to all nodes with the higher score indicating better placement(change to lower)
def score_nodes(trait_dict):
    priority_weight = 0.5
    rank_weight = 0.4
    level_weight = 0.1
    max_score = 105
    modifier = 5

    for trait in trait_dict:
        lst = trait_dict.get(trait)
        priority_val = modifier * (len(priority_list) - priority_list.index(trait))/len(priority_list)
        rank_max = int(lst[-1].trait.split(' ')[0].strip(' +%'))
        
        if len(lst) == 0: 
            continue
        
        # level ups at: 1,4,8,13
        for skill in lst:
            level_val = skill.req[0].strip("Level ")
            if level_val == "Specia":
                skill.score = 1000
                continue

            level_val = modifier - ((modifier/4) * (int(level_val)//4))
            rank_val = modifier * int(skill.trait.split(' ')[0].strip(' +%')) / rank_max
            score_val = '%.2f'%((priority_weight * priority_val) + (rank_weight * rank_val) + (level_weight * level_val))
            
            # # conditionals(modifications to score)
            # t = skill.trait.lower()
            # if " to " in t:
            #     # EX: +6% speed to Fast attack
            #     skill.score = max_score - int(round(float(score_val) * 10,0))
            # elif " vs " in t:
            #     # EX: +40% Glory VS opponents of lower level
            #     skill.score = max_score - int(round(float(score_val) * 10,0))
            # elif " when " in t:
            #     # EX: +6 Stamina when winning
            #     skill.score = max_score - int(round(float(score_val) * 10,0))
            # elif " for " in t:
            #     # EX: +4 Dominance for first 15 seconds
            #     skill.score = max_score - int(round(float(score_val) * 10,0))
            # elif " while " in t:
            #     # EX: +4 Defense while blocking
            #     skill.score = max_score - int(round(float(score_val) * 10,0))
            # elif " random " in t:
            #     # EX: +4 Damage at random intervals
            #     skill.score = max_score - int(round(float(score_val) * 10,0))
            # else:
            #     skill.score = max_score - int(round(float(score_val) * 10,0))
            
            skill.score = max_score - int(round(float(score_val) * 10,0))

            # print statements
            # print(f"P:{modifier} * {(len(priority_list) - priority_list.index(trait))}/{len(priority_list)} = {priority_val}") #priority
            # print(f"R:{modifier} * {int(skill.trait.split(' ')[0].strip(' +%'))} / {rank_max} = {rank_val}") #rank
            # print(f"L:{modifier} - {(modifier/4)} * {(int(level_val)//4)} = {level_val}") #level
            # print(f"{skill.name}[{100-skill.score}] = ({priority_weight} * {priority_val}) + ({rank_weight} * {rank_val}) + ({level_weight} * {level_val})")
        # print("\n")

def primary_sort(list):
    for node in list:
        if len(node.req) == 1:
            list.remove(node)
            list.insert(0,node)  


###############################################################################################
#                                   TRAIT LIST FUNCTIONS
###############################################################################################
def add_trait(node):
    if "health" in node.trait.lower():
        trait_dict["health"].append(node)
    elif "dominance" in node.trait.lower():
        trait_dict["dominance"].append(node)
    elif "damage" in node.trait.lower():
        trait_dict["damage"].append(node)
    elif "defense recovery" in node.trait.lower():
        trait_dict["defense recovery"].append(node)
    elif "stamina recovery" in node.trait.lower():
        trait_dict["stamina recovery"].append(node)
    elif "stamina" in node.trait.lower():
        trait_dict["stamina"].append(node)
    elif "money" in node.trait.lower():
        trait_dict["wealth"].append(node)
    elif "glory" in node.trait.lower():
        trait_dict["glory"].append(node)
    elif "speed" in node.trait.lower():
        trait_dict["speed"].append(node)
    elif "defense" in node.trait.lower():
        trait_dict["defense"].append(node)
    else:
        # print(f"Failed {node.name}")
        node.score = 1
        return


###############################################################################################
#                                   PRINTING FUNCTIONS
###############################################################################################
def print_nary_tree(node, depth=0, showScore=False):
    if node:
        # Print the current node's value at the current depth
        print("    ",end="")
        if showScore:
            print("    " * depth + "#" + str(node.num) + " " + str(node.name) + " (" + str(node.score) + ")" "_" + str(node.depth))
        else: 
            print("    " * depth + str(node.name) + "_" + str(node.depth))

        # Recursively print the children of the current node
        for child in node.children:
            print_nary_tree(child, depth + 1, showScore)

def print_list(list, showScores = False):
    print("List: [",end="")
    if showScores:
        for node in list:
            print(node.name,"(",node.score,")",end=", ")
    else: 
        for node in list:
            print(node.name,end=", ")
    print("]")

def print_dict(dictionary):
    print(f"List: [",end="")
    for _, value in dictionary.items():
        print(f"{value.name}",end=", ")
    print(f"] Length: {len(dictionary)}")

###############################################################################################
#                                   NEW FUNCTIONS
###############################################################################################
# returns path required to get to a node
def find_path(root, target_name, list):
    if root is None:    
        return None
    list.append(root)

    if target_name == root.name:
        return True

    for child in root.children:
        child_path = find_path(child, target_name, list)
        if child_path:
            return True

    # If the target is not found in any child, return an empty list
    list.pop(-1)
    return None

###############################################################################################
#                                  OPTIMIZATION FUNCTIONS
###############################################################################################
"""
    can make code more efficient by filtering if it list has all cat_
"""
def find_connected_subtrees(root, k):
    def generate_subtrees(node):
        if not node:
            return []

        subtrees = []
        
        # base + 6 cat_s
        if k == 1:
            return root
        
        # Explore all combinations of nodes starting from the current node
        for combo in get_combos(get_descendants(node, k), k):
            if root not in combo:
                break
            subtree = list(combo)
            subtree.pop(0)
            if is_connected(subtree):
                if discriminate(subtree):
                    print([node.name for node in subtree],sum([node.score for node in subtree]))
                    subtrees.append(subtree)
        return subtrees

    def get_descendants(node, k):
        """ returns list of valid nodes within depth"""
        descendants = []
        stack = [node]
        while stack:
            current_node = stack.pop()
            if current_node.depth <= (k+1):
                descendants.append(current_node)
                stack.extend(child for child in current_node.children if child not in descendants)
            # else:
                # print(f'skipped {current_node.name} @ depth{current_node.depth}')
        
        # remove root and cat_s as going to hardcode it in 
        for n in node.children:
            descendants.remove(n)
        return descendants

    def is_connected(subtree):
        """Checks if a list of nodes is connected through their depth and children"""
        subtree = sorted(subtree, key=lambda x: x.depth)
        # print("values",[node.score for node in subtree])
        # print("depths",[node.depth for node in subtree])
        # print(sorted)
        curr_depth = 3
        depth_list = []

        # change list to start and end pointers
        if not subtree:
            print("Nones")
            return False
        
        # ascending connected depths: 1,2,3
        for node in subtree:
            # same depth
            if curr_depth == node.depth:
                depth_list.append(node)

            # new depth encountered
            elif (curr_depth +1)  == node.depth:
                # check list to see if sorted[i] is a child of any
                found = False
                
                for j in depth_list:
                    if node in j.children:
                        found = True

                if not found:
                    # print("False 1")
                    return False
                curr_depth +=1
                depth_list = [node]               
            
            # disconnected node
            else:
                return False
            
        return True
    
    def discriminate(li):
        frequency_dict = dict.fromkeys(class_list, 0)
        # Count the frequency of each number in the array
        for n in li:
            if n.depth == 3:
                frequency_dict[n.type] += 1
        
        if frequency_dict['cat_Religion'] != 1:
            return False
        if frequency_dict['cat_Clan'] != 1:
            return False
        if frequency_dict['cat_Personality'] != 1:
            return False
        return True
        
    
    def get_combos(node_list, k):
        """combinations() but always include reqs as to increase efficiency
            need to replace 7 nodes in indices to have base and 6 cat_s

            change node.nums

        """        
        # combinations('ABCD', 2) --> AB AC AD BC BD CD
        # combinations(range(4), 3) --> 012 013 023 123
        pool = tuple(node_list)
        # print([s.name for s in pool])
        n = len(pool)
        if k > n:
            return
        indices = list(range(k))
        yield tuple(pool[i] for i in indices)
        while True:
            for i in reversed(range(k)):
                if indices[i] != i + n - k:
                    break
            else:
                return
            indices[i] += 1
            for j in range(i+1, k):
                indices[j] = indices[j-1] + 1
            yield tuple(pool[i] for i in indices)
    
    # Explore all nodes in the tree to find connected subtrees
    return generate_subtrees(root)

# helper function
def find_best(root, k):
    # k also includes all cat_ and base(+7)
    max = 100
    best = []
    best_score = []
    k += 1
    subtrees = find_connected_subtrees(root, k)
    for subtree in subtrees:
        subtree_score = [node.score for node in subtree]
        # print(subtree_names,sum(subtree_names))
        if sum(subtree_score) < max:
            best = [node.name for node in subtree]
            best_score = subtree_score
            max = sum(subtree_score)
    print("best", best)
    print("best_score",best_score)
    print("max: ", max)

###############################################################################################
#                                   DRIVER CODE
###############################################################################################
head = TreeNode("base",None,None)
node_list = []

if not os.path.isfile(file_path):
    open(file_path, "x")

if os.path.getsize(file_path) == 0:
    response = requests.get(url)
    response.raise_for_status()
    file = open(file_path, "wb")
    file.write(response.content)
    file.close()
    
    # Parse the HTML content with Beautiful Soup
    soup = BeautifulSoup(response.text, "html.parser")
    print("Read from webpage")
else:
    # Read from file if 
    with open(file_path, 'r', encoding='utf-8') as file:
        # Parse the HTML content of the file using Beautiful Soup
        soup = BeautifulSoup(file, 'html.parser')
    print("Read from file")
for class_name in class_list:
    # Find all HTML elements with the specified class
    elements_with_class = soup.find_all(class_=class_name)
    # print(f"\nText content from class '{class_name}':")
    class_node = TreeNode(class_name, None, None)
    add_node(head,class_node,None)
    for element in elements_with_class:
        # print(f"{element}")  # Use .strip() to remove leading/trailing whitespace
        name = element.find('h2').text
        # print(f"    {element.find('h4').text}")
        req = element.find('p').text[14:].split(", ")
        trait = element.find('p').find_next_sibling('p').find_next_sibling('p').text
        if len(trait) == 0: 
            trait = "N/A"
        
        # print(f"name: \"{name}\"")
        # print(f"    req: \"{req}\"")
        # print(f"    trait: \"{trait}\"")
        new_node = TreeNode(name, req, trait)
        node_list.append(new_node)
        add_trait(new_node)
    
    # sort the node list by req
    primary_sort(node_list)

    #loops unadded nodes to trees until added
    for node in node_list:
        add_node(class_node, node, node_list)
    node_list = []

size = assign_num(head)
# sorting alphabetically does not work, sort by convert to number then sort
for key in trait_dict:
    trait_dict[key].sort(key=lambda x: float(x.trait.split(" ", 1)[0].replace("%","")))

score_nodes(trait_dict)
print_nary_tree(head, 0, True)

find_best(head, 4)
