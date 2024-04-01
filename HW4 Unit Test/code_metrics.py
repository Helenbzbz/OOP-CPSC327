import ast
import sys

def main():
    '''
    Main function that reads the content of the files passed as arguments and analyzes them.
    Input: Files to analyze
    Output: Complexity of the functions in the files
    '''
    ## iterates over command-line arguments passed to the script (excluding the script name itself).
    for filename in sys.argv[1:]:  
        with open(filename, 'r') as file:
            ## Read Content, get the tree and analyze it
            content = file.read()
            tree = ast.parse(content, filename=filename)
            analyze_tree(tree)

def analyze_tree(tree):
    '''
    Analyze the tree and print the complexity of each function under child node.
    Input: Tree
    Output: Complexity of the functions in the tree
    '''
    ### Iterates over the nodes of the tree
    for node in ast.iter_child_nodes(tree):
        ## If the node is a class, we dive deeper
        if isinstance(node, ast.ClassDef):
            # Update the current class name
            class_name = node.name  
            # Analyze the functions in the class
            for child_node in ast.iter_child_nodes(node):
                # Check if the child node is a function, if so, analyze it
                if isinstance(child_node, ast.FunctionDef):
                    analyze_function(child_node, class_name)
        ## If the node is a function, we analyze
        elif isinstance(node, ast.FunctionDef):
            analyze_function(node)

def analyze_function(node, class_name=None):
    '''
    Analyze the function and print the complexity of the function.
    Input: Function node
    Output: Complexity of the function
    '''
    ### Calculate the number of lines and complexity of the function
    lines = len({n.lineno for n in ast.walk(node) if hasattr(n, 'lineno')})
    ### Calculate the complexity of the function, get the name prefix, and print the result
    complexity = calculate_complexity(node)
    name_prefix = f"{class_name}." if class_name else ""
    print(f"{name_prefix}{node.name}, Line count: {lines-1}, Complexity: {complexity}")

def calculate_complexity(node):
    '''
    Calculate the complexity of the function.
    Following the McCabe complexity formula:
     1. Start with a complexity of 1
     2. Add 1 for each if, for, while, or try statement.
     3. Add the number of boolean operators in the function.
     4. Add 1 for each comprehension and generator expression.
     5. Add 1 for each exception handler.
    '''
    complexity = 1
    for n in ast.walk(node):
        ## Check if the node is an if, for, while, or try statement
        if isinstance(n, (ast.If, ast.For, ast.While, ast.Try)):
            complexity += 1
        ## Check if the node is a boolean operator
        elif isinstance(n, ast.BoolOp):
            complexity += len(n.values) - 1
        ## Check if the node is a comparison operator
        elif isinstance(n, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            complexity += 1 + sum(isinstance(e, ast.IfExp) for e in ast.walk(n))
        ## Check if the node is an exception handler
        elif isinstance(n, ast.ExceptHandler):
            complexity += 1
    return complexity

if __name__ == "__main__":
    main()

