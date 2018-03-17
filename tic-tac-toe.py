import random
import datetime


class Team5(object):

    def __init__(self):
        self.inf=100000000
        self.depth=3
        self.buffer={}
        self.begin = datetime.datetime.utcnow()
        self.timelimit = datetime.timedelta(seconds=15.8)

    def enemy(self,flag):
        if flag=='x':
            return 'o'
        return 'x'

    def reset(self,board,cell):
        board.board_status[cell[0]][cell[1]] = '-'
        board.block_status[cell[0] / 4][cell[1] / 4] = '-'

    def ticktock(self, a):
        return a - self.begin > self.timelimit

    def heuristic(self,board,flag,depth):
        utility=0
        for i in range(4):
            for j in range(4):
                if board.block_status[i][j]==flag:
                    if [i,j] in [[0,0],[0,3],[3,0],[3,3]]:
                        utility+=100
                    elif [i,j] in [[0,1],[0,2],[1,0],[2,0],[1,3],[2,3],[3,1],[3,2]]:
                        utility+=40
                    else:
                        utility+=20

                elif board.block_status[i][j]==self.enemy(flag):
                    if [i,j] in [[0,0],[0,3],[3,0],[3,3]]:
                        utility-=100
                    elif [i,j] in [[0,1],[0,2],[1,0],[2,0],[1,3],[2,3],[3,1],[3,2]]:
                        utility-=40
                    else:
                        utility-=20

                if board.block_status[i][j]=='-':
                    temp=[[0 for _ in range(4)] for _ in range(4)]
                    for x in range(4):
                        for y in range(4):
                            temp[x][y]=board.board_status[4*i+x][4*j+y]

                    utility += self.update_heuristic(temp,flag)
                    utility -= self.update_heuristic(temp, self.enemy(flag))

        utility += 10*self.update_heuristic(board.block_status,flag) - 0.01*depth
        utility -= 10*self.update_heuristic(board.block_status, self.enemy(flag))+0.01*depth
        return utility

    def update_heuristic(self,block,flag):
        four = [(1,1),(1,2),(2,1),(2,2)]
        three = [(0,1),(0,2),(1,0),(1,3),(2,0),(2,3),(3,1),(3,2)]
        two = [(0,0),(0,3),(3,0),(3,3)]

        hash_block = tuple([ tuple(block[i]) for i in range(4)])
        if (hash_block,flag) in self.buffer:
            return self.buffer[hash_block, flag]

        diamond = [0 for i in range(4)]
        diamond[0] = [[1,2],[2,1],[2,3],[3,2]]
        diamond[1] = [[1,1],[2,2],[2,0],[3,1]]
        diamond[2] = [[0,2],[1,1],[1,3],[2,2]]
        diamond[3] = [[0,1],[1,0],[1,2],[2,1]]

        enemy = self.enemy(flag)
        utility=0

        array = [[0,-10,-50,-250,-1250],[10,0,0,0,0],[50,0,0,0,0],[250,0,0,0,0],[1250,0,0,0,0]]

        for i in range(4):
            count = 0
            enemy_count = 0

            for j in range(4):
                if block[i][j]==flag:
                    count+=1
                elif block[i][j]==enemy:
                    enemy_count+=1

            utility+=array[count][enemy_count]


        for i in range(4):
            count = 0
            enemy_count = 0

            for j in range(4):
                if block[j][i]==flag:
                    count+=1
                elif block[j][i]==enemy:
                    enemy_count+=1

            utility += array[count][enemy_count]


        for i in diamond:
            count=0
            enemy_count=0
            for j in i:
                x=j[0]
                y=j[1]
                if block[x][y]==flag:
                    count+=1
                elif block[x][y]==enemy:
                    enemy_count+=1

            utility += array[count][enemy_count]

        self.buffer[hash_block,flag] = utility
        return utility


    def prune(self,board,old_move,alpha,beta,ismax,flag,depth,maxdepth,new_pos):

        if self.ticktock(datetime.datetime.utcnow()):
            return (0,(-1,-1))

        else:
            states = board.find_terminal_state()
            if states[1]=="WON":
                if states[0]==flag:
                    return (1000,old_move)
                return (-1000,old_move)

            if maxdepth==depth:
                value=self.heuristic(board,flag,maxdepth)
                return (value,old_move)

            valid_cells = board.find_valid_move_cells(old_move)
            if len(valid_cells) == 0:
                value = self.heuristic(board, flag, maxdepth)
                return (value, old_move)
            random.shuffle(valid_cells)

            for cell in valid_cells:
                if ismax:
                    board.update(old_move,cell,flag)

                    value = self.prune(board,cell,alpha,beta,0,flag,depth,maxdepth+1,new_pos)

                    if self.ticktock(datetime.datetime.utcnow()):
                        self.reset(board,cell)
                        return (0,(-1,-1))

                    if value[0] > alpha:
                        alpha=value[0]
                        new_pos=cell
                    self.reset(board,cell)

                else:
                    board.update(old_move, cell, self.enemy(flag))

                    value = self.prune(board, cell, alpha, beta, 1, flag, depth, maxdepth + 1,new_pos)

                    if self.ticktock(datetime.datetime.utcnow()):
                        self.reset(board, cell)
                        return (0, (-1, -1))

                    if value[0] < beta:
                        beta = value[0]
                        new_pos=cell

                    self.reset(board, cell)
                if alpha>=beta:
                    break
            if ismax:
                return (alpha,new_pos)
            else:
                return (beta,new_pos)

    def move(self, board, old_move, flag):

        self.timelimit = datetime.timedelta(seconds=15.8)
        self.begin = datetime.datetime.utcnow()
        self.depthi = 3
        value=''
        while not(self.ticktock(datetime.datetime.utcnow())) and self.depthi<9:
            ans = self.prune(board,old_move,-self.inf,self.inf,1,flag,self.depthi,0,(0,0))
            if ans[1]!=(-1,-1):
                value=ans[1]
            self.depthi+=1
        return value
