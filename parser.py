
import ast
from pprint import pprint
class Block():
    # Block tags
    NORMAL = 0
    LOOP_HEADER = 1
    def __init__(self):
   
        self.next_block = None
        self.has_return = False
        self.start_line_no = 0
        self.statements = []
        self.exit_blocks = []
        self.marked = False
        self.tag = Block.NORMAL
        self.dependents = []
        
    def copy_dict(self, copy_to):
    
        for dependent in self.dependents:
            dependent.__dict__ = copy_to.__dict__
        self.__dict__ = copy_to.__dict__
        copy_to.dependents = self.dependents + [self]

F_BLOCK_LOOP = 0
F_BLOCK_EXCEPT = 1
F_BLOCK_FINALLY = 2
F_BLOCK_FINALLY_END = 3

class ControlFlowGraph(AstFullTraverser):
    def __init__(self):
        self.current_block = None
        self.frame_blocks = []
        self.current_line_num = 0
        
    def parse_ast(self, source_ast):
        self.run(source_ast)
        return source_ast
        
    def parse_file(self, file_path):
        source_ast = self.file_to_ast(file_path)
        return self.parse_ast(source_ast)
        
    def file_to_ast(self, file_path):
        s = self.get_source(file_path)
        return ast.parse(s, filename = file_path, mode = 'exec')
    
    def get_source(self, fn):
        try:
            f = open(fn,'r')
            s = f.read()
            f.close()
            return s
        except IOError:
            return ''
        
    def push_frame_block(self, kind, block):
        self.frame_blocks.append((kind, block))

    def pop_frame_block(self, kind, block):
        actual_kind, old_block = self.frame_blocks.pop()
        assert actual_kind == kind and old_block is block, \
    def is_empty_block(self, candidate_block):
        return not candidate_block.statements
            
    def check_child_exits(self, candidate_block, after_control_block):
    
        if candidate_block.has_return:
            return
        if self.is_empty_block(candidate_block):
            candidate_block.copy_dict(after_control_block)
            return
        if not after_control_block in candidate_block.exit_blocks:
            candidate_block.exit_blocks.append(after_control_block)
    def add_to_block(self, node):
        if not self.current_block:
            return
        if self.current_line_num >= node.lineno:
            return   
        if isinstance(node, ast.While) or isinstance(node, ast.For):
            if not self.is_empty_block(self.current_block):
                test_block = self.new_block()
                self.current_block.exit_blocks.append(test_block)
                self.use_next_block(test_block)
        self.current_line_num = node.lineno
        for f_block_type, f_block in reversed(self.frame_blocks):
            if f_block_type == F_BLOCK_EXCEPT:
                self.current_block.statements.append(node)
                for handler in f_block:
                    self.current_block.exit_blocks.append(handler)
                if isinstance(node, ast.While) or isinstance(node, ast.For):
                    break
                next_statement_block = self.new_block()
                self.current_block.exit_blocks.append(next_statement_block)
                self.use_next_block(next_statement_block)
                break
        else:
            self.current_block.statements.append(node)
    def run(self, root):
        self.visit(root)
    def new_block(self):
        return Block()
    def use_block(self, block):
        self.current_block = block
    def empty_block(self, block):
        return not block.statements
    def use_next_block(self, block=None):
        if block is None:
            block = self.new_block()
        self.current_block.next_block = block
        self.use_block(block)
        return block
    def add_to_exits(self, source, dest):
        source.exit_blocks.append(dest)
    def visit(self, node):
        if self.check_has_return():
            return
        self.check_block_num(node)
        self.add_to_block(node)
        method = getattr(self, 'do_' + node.__class__.__name__)
        return method(node)
    def check_block_num(self, node):
          if not self.current_block:
            return
        if not self.current_block.start_line_no:
            self.current_block.start_line_no = node.lineno
            print(self.current_block.start_line_no )
    def check_has_return(self):
        return self.current_block and self.current_block.has_return
    def do_FunctionDef(self, node):
        block = self.new_block()
        self.use_block(block)
        node.initial_block = block
        self.exit_block = self.new_block()
        self.exit_block.start_line_no = "Exit"
        for z in node.body:
            self.visit(z)
        for e in self.current_block.exit_blocks:
            if e.start_line_no == "Exit":
                return
        else:
            self.check_child_exits(self.current_block, self.exit_block)
            
    def do_If(self, node):
        ''' If an if statement is the last in a straight line then an empty
            and unused block will be created as the after_if. '''
        if_block = self.current_block
        after_if_block = self.new_block()
        # Then block
        then_block = self.new_block()
        self.add_to_exits(if_block, then_block)
        self.use_block(then_block)
        for z in node.body:
            self.visit(z)
        # Make sure the then exits point to the correct place
        self.check_child_exits(self.current_block, after_if_block)
        # Else block
        if node.orelse:
            else_block = self.new_block()
            self.add_to_exits(if_block, else_block)
            self.use_block(else_block)
            for z in node.orelse:
                self.visit(z)
            # Make sure the else exits point to the correct place
            self.check_child_exits(self.current_block, after_if_block)
        else:
            self.add_to_exits(if_block, after_if_block)
        # Set the next block of the if to the after_if block
        if_block.next = after_if_block
        self.use_block(after_if_block)
        
    def do_While(self, node):
        self.do_Loop(node)
        
    def do_For(self, node):
        self.do_Loop(node)
        
    def do_Loop(self, node):
     
        test_block = self.current_block
            
        test_block.tag = Block.LOOP_HEADER
        self.push_frame_block(F_BLOCK_LOOP, test_block)

        after_loop_block = self.new_block()
        loop_body_block = self.new_block()
        self.add_to_exits(test_block, loop_body_block)
        test_block.next = after_loop_block
        self.use_block(loop_body_block)
        for z in node.body:
            self.visit(z)
        self.check_child_exits(self.current_block, test_block)
        self.pop_frame_block(F_BLOCK_LOOP, test_block)
        
        if node.orelse:
            else_body = self.new_block()
            self.add_to_exits(test_block, else_body)
            self.use_block(else_body)
            else_body.next = after_loop_block
            for z in node.orelse:
                self.visit(z)
            self.check_child_exits(self.current_block, after_loop_block)
        else:
            self.add_to_exits(test_block, after_loop_block)
        
        self.use_next_block(after_loop_block)
        
        
if __name__ == '__main__':
    cfg = ControlFlowGraph()
    s_ast = cfg.parse_file(fn)
    PrintCFG(s_ast)