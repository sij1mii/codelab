
tree = ('+',
       ('*', 3, 4),
       ('-', 10, ('*',
                  2,
                  3)))

large_tree = 1
for i in xrange(15):
    large_tree = ('+', large_tree, large_tree)

deep_tree = 1
for i in xrange(1000):
    deep_tree = ('+', deep_tree, 1)


def eval(tree):
    if not isinstance(tree, tuple):
        return tree
    op = tree[0]
    if op == '+':
        return evalAdd(tree[1], tree[2])
    elif op == '-':
        return evalSub(tree[1], tree[2])
    elif op == '*':
        return evalMul(tree[1], tree[2])
    else:
        raise Exception('Unexpected op')

def evalAdd(left, right):
    return eval(left) + eval(right)

def evalSub(left, right):
    return eval(left) - eval(right)

def evalMul(left, right):
    return eval(left) * eval(right)


print 'eval(tree) ==', eval(tree)

###########################################


class EvalTask(object):
    def __init__(self, tree):
        self.__tree = tree

    def start(self, cont):
        tree = self.__tree
        if not isinstance(tree, tuple):
            cont.done(tree)
            return
        op, left, right = tree
        if op == '+':
            task = AddTask(left, right)
        elif op == '-':
            task = SubTask(left, right)
        elif op == '*':
            task = MulTask(left, right)
        else:
            raise Exception('Unexpected op')
        cont.call(task, 'wait')

    def resume(self, cont, state, response):
        assert state == 'wait'
        cont.done(response)


class AddTask(object):
    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    def start(self, cont):
        cont.call(EvalTask(self.__left), 'left')

    def resume(self, cont, state, response):
        if state == 'left':
            self.left_res = response
            cont.call(EvalTask(self.__right), 'right')
        else:
            assert state == 'right'
            cont.done(self.left_res + response)


class SubTask(object):
    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    def start(self, cont):
        cont.call(EvalTask(self.__left), 'left')

    def resume(self, cont, state, response):
        if state == 'left':
            self.left_res = response
            cont.call(EvalTask(self.__right), 'right')
        else:
            assert state == 'right'
            cont.done(self.left_res - response)


class MulTask(object):
    def __init__(self, left, right):
        self.__left = left
        self.__right = right

    def start(self, cont):
        cont.call(EvalTask(self.__left), 'left')

    def resume(self, cont, state, response):
        if state == 'left':
            self.left_res = response
            cont.call(EvalTask(self.__right), 'right')
        else:
            assert state == 'right'
            cont.done(self.left_res * response)


class Controller(object):
    def __init__(self, runner, task, callstack):
        self.__runner = runner
        self.__task = task
        self.__stack = callstack

    def call(self, task, state):
        stack = ((self.__task, state), self.__stack)
        self.__runner.push_call(stack, task)

    def done(self, response):
        self.__runner.push_done(self.__stack, response)


class Runner(object):
    def __init__(self, task):
        # tasks is FIFO to run tasks in DFS way.
        # To run tasks in BFS way, use collections.deque.
        self.__tasks = [('call', None, task)]
        self.response = None
        self.done = False

    def run(self):
        while self.__tasks:
            self.run_internal()

    def __push_task(self, task):
        self.__tasks.append(task)

    def push_call(self, callstack, subtask):
        self.__push_task(('call', callstack, subtask))

    def push_done(self, callstack, response):
        self.__push_task(('done', callstack, response))

    def run_internal(self):
        task = self.__tasks.pop()
        type = task[0]
        stack = task[1]
        if type == 'call':
            f = task[2]
            cont = Controller(self, f, stack)
            f.start(cont)
        else:
            # 'done'
            response = task[2]
            if not stack:
                self.response = response
                self.done = True
            else:
                parent_stack = stack[1]
                task, state = stack[0]
                cont = Controller(self, task, parent_stack)
                task.resume(cont, state, response)


runner = Runner(EvalTask(tree))
runner.run()
print 'runner.response =', runner.response
