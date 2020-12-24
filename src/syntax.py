class SyntaxTreeNode(object):
    '''Syntax tree node'''

    def __init__(self, value = None, _type = None, extra_info = None):
        # The value of the node, which is terminal or non-terminal in grammar.
        self.value = value
        # Register the types of certain tokens.
        self.type = _type
        # Some other information about the token is recorded in the semantic analysis, such as that the keyword is a variable and the variable type is int
        self.extra_info = extra_info
        self.father = None
        self.left = None
        self.right = None
        self.first_son = None

    def set_value(self, value):
        self.value = value

    def set_type(self, _type):
        self.type = _type

    def set_extra_info(self, extra_info):
        self.extra_info = extra_info


class SyntaxTree(object):
    '''Syntax tree'''

    def __init__(self):
        # Tree root node
        self.root = None
        # The node that is now traversed
        self.current = None

    # To add a child node, you need to make sure the parent is in the tree
    def add_child_node(self, new_node, father=None):
        if not father:
            father = self.current
        
        # Recognize the ancestors
        new_node.father = father
        # If the parent node has no child, assign it to its first child
        if not father.first_son:
            father.first_son = new_node
        else:
            current_node = father.first_son
            while current_node.right:
                current_node = current_node.right
            
            current_node.right = new_node
            new_node.left = current_node
        self.current = new_node

    # Swap two adjacent sister subtrees
    def switch(self, left, right):
        left_left = left.left
        right_right = right.right
        left.left = right
        left.right = right_right
        right.left = left_left
        right.right = left
        if left_left:
            left_left.right = right
        
        if right_right:
            right_right.left = left

