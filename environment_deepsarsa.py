import time
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image

PhotoImage = ImageTk.PhotoImage
UNIT = 50  # 픽셀 수
HEIGHT = 5  # 그리드 세로
WIDTH = 5  # 그리드 가로

np.random.seed(1)
ㄴ

class Env(tk.Tk):
    def __init__(self, render_speed=0.01):
        super(Env, self).__init__()
        self.render_speed=render_speedㄴ
        self.action_space = ['u', 'd', 'l', 'r']
        self.action_size = len(self.action_space)
        self.title('DeepSARSA')
        self.geometry('{0}x{1}'.format(WIDTH * UNIT+20, HEIGHT * UNIT+10))  # 그리드 바깥쪽 여백
        self.shapes = self.load_images()  # '../img' 에서 이미지를 가져옴, 리턴수만큼 받아야하는데 그렇지 않은경우 리스트로 0,1,2로 받음
        self.canvas = self._build_canvas()  # 설정해준 그리드와 배경을 객체화
        self.counter = 0
        self.rewards = []
        self.goal = []
        # 장애물이 처음 등장하는 위치를 설정
        self.set_reward([0, 1], -1)
        self.set_reward([1, 2], -1)
        self.set_reward([2, 3], -1)
        # 처음 등장하는 목표의 위치
        self.set_reward([4, 4], 1)

    def _build_canvas(self):  # 배경과 그리드를 설정
        canvas = tk.Canvas(self, bg='white',
                           height=HEIGHT * UNIT,
                           width=WIDTH * UNIT)
        # 그리드 생성
        for w in range(0, WIDTH * UNIT, UNIT):  # 0부터 픽셀수*넓이를 픽셀수만큼
            x0, y0, x1, y1 = w, 0, w, HEIGHT * UNIT
            canvas.create_line(x0, y0, x1, y1)
        for h in range(0, HEIGHT * UNIT, UNIT):  # 0부터 픽셀수*높이를 픽셀수만큼 나눠주고 나눈 부분의 0부터 픽셀수*넓이까지 그리드를 그려준다.
            x0, y0, x1, y1 = 0, h, WIDTH * UNIT, h
            canvas.create_line(x0, y0, x1, y1)
            
#         self.rewards = []  # 보상을 저장
#         self.goal = []  # 목표를 저장
        
        # 캔버스에 이미지 추가
        w, h = UNIT/2, UNIT/2
        self.rectangle = canvas.create_image(w, h, image=self.shapes[0])  # 사각형이 처음 등장하는 위치의 좌표값이고 이거에 대한 St 상태값의 위치를 넣어줌

        canvas.pack()  # 그려진 모든걸 tk(윈도우창)에 띄워주는 함수

        return canvas

    def load_images(self):  # 이미지를 불러옴
        rectangle = PhotoImage(
            Image.open("../img/rectangle.png").resize((30, 30)))
        triangle = PhotoImage(
            Image.open("../img/triangle.png").resize((30, 30)))
        circle = PhotoImage(
            Image.open("../img/circle.png").resize((30, 30)))

        return rectangle, triangle, circle

    def reset_reward(self):

        for reward in self.rewards:  # set_rewards에서 append 된 self.rewards를
            self.canvas.delete(reward['figure'])  # reward 내의 figure 키의 값들을 삭제해준다.

        self.rewards.clear()
        self.goal.clear()
        self.set_reward([0, 1], -1)
        self.set_reward([1, 2], -1)
        self.set_reward([2, 3], -1)

        # goal
        self.set_reward([4, 4], 1)

    def set_reward(self, state, reward):
        state = [int(state[0]), int(state[1])]  # set_reward([0, 1], -1)
        x = int(state[0])
        y = int(state[1])
        # 빈딕셔너리 선언
        temp = {}
        if reward > 0:
            temp['reward'] = reward
            temp['figure'] = self.canvas.create_image((UNIT * x) + UNIT / 2,
                                                       (UNIT * y) + UNIT / 2,
                                                       image=self.shapes[2])

            self.goal.append(temp['figure'])  # 보상이 0보다 클때는 goal에 딕셔너리를 먼저 한번 저장해준다.


        elif reward < 0:  # set_reward([0, 1], -1)이므로 reward는 -1 이므로 0보다 작으므로 이걸 실행
            temp['direction'] = -1  # 딕셔너리안에 각각 값을 저장
            temp['reward'] = reward
            temp['figure'] = self.canvas.create_image((UNIT * x) + UNIT / 2,  # 각 그리드의 중앙을 찾아줌
                                                      (UNIT * y) + UNIT / 2,  # create_image()는 (UNIT * x) + UNIT / 2, (UNIT * y) + UNIT / 2, image=self.shapes[1])를 임의의 숫자로 지정해주는
                                                      image=self.shapes[1])

        temp['coords'] = self.canvas.coords(temp['figure'])  # coords()는 임의의 숫자로 지정된 temp['figure']를 (UNIT * x) + UNIT / 2, (UNIT * y) + UNIT / 2, image=self.shapes[1])로 반환
        temp['state'] = state
        self.rewards.append(temp)

    # new methods
    def check_if_reward(self, state):
        check_list = dict()
        check_list['if_goal'] = False  # {'if_goal' : False}
        rewardsss = 0

        for reward in self.rewards:  # 딕셔너리들을 반복해서
            if reward['state'] == state:  # 딕셔너리 안에 state 값이 check_if_reward(self, state)의 state값과 같다면
                rewardsss += reward['reward']  # 위에 0인 rewardsss에 reward의 reward 값을 더해주고
                if reward['reward'] == 1:  # reward가 1일때, 즉 O에 도착해서 1을 받았으면
                    check_list['if_goal'] = True  # if_goal을 True로 바꿔준다.

        check_list['rewards'] = rewardsss  # 더해진 rewardsss를 rewards키에 넣어준다.

        return check_list  # {'if_goal' : 00, 'rewards' : 00 } 값이 리턴

    def coords_to_state(self, coords):
        x = int((coords[0] - UNIT / 2) / UNIT)
        y = int((coords[1] - UNIT / 2) / UNIT)
        return [x, y]

    def reset(self):
        self.update()
        time.sleep(0.5)
        x, y = self.canvas.coords(self.rectangle)  # 사각형의 위치값을 x, y
        self.canvas.move(self.rectangle, UNIT / 2 - x, UNIT / 2 - y)  # 이 x,y 를 지우고 픽셀나누면 초기 50, 50 위치로 이동하게된다.
        self.reset_reward()  # 위에 리셋함수를 실행하고
        return self.get_state()  # 겟스테이트를 리턴
    
    def step(self, action):
        self.counter += 1
        self.render()

        if self.counter % 2 == 1:  # 네모가 두번 움직일때 세모가 한번움직이는
            self.rewards = self.move_rewards()  # move_rewards함수에서 new_rewards를 리턴받는다.

        next_coords = self.move(self.rectangle, action)  # action으로 주어진 0,1,2,3 에 따라 네모를 옴겨주고 그 값을 반환
        check = self.check_if_reward(self.coords_to_state(next_coords))  # {'if_goal' : T or F , 'rewards' : 값 }
        done = check['if_goal']  # T 또는 F
        reward = check['rewards']  # 값 
        
        self.canvas.tag_raise(self.rectangle)  # 세모와 네모가 겹쳤을때 네모를 위로 올려주는

        s_ = self.get_state()

        return s_, reward, done

    def get_state(self):

        location = self.coords_to_state(self.canvas.coords(self.rectangle))  ## 위에 천천히 읽어보면 서로 들어가는거보면 그리드 xy좌표를 알수잇음
        agent_x = location[0]  # 네모의 x위치
        agent_y = location[1]  # 네모의 y위치

        states = list()

        for reward in self.rewards:
            reward_location = reward['state']  # 삼각형의 위치[x,y] 값
            states.append(reward_location[0] - agent_x)  # 삼각형의 x값에 에이전트 x값을 빼준다.
            states.append(reward_location[1] - agent_y)  # 삼각형의 y값에 에이전트 y값을 빼준다.
            if reward['reward'] < 0:
                states.append(-1) 
                states.append(reward['direction'])  # reward에는 [reward_location[0] - agent_x, reward_location[1] - agent_y, -1, -1]
            else:
                states.append(1)  # reward에는 [reward_location[0] - agent_x, reward_location[1] - agent_y, 1]

        return states  # 리스트 states를 리턴

    def move_rewards(self):
        new_rewards = []  # 리스트선언
        for temp in self.rewards:  # 딕셔너리를 돌림 동그라미 하나 세모 세개
            if temp['reward'] == 1:  # 동그라미 딕셔너리일때
                new_rewards.append(temp)  # 리스트에 동그라미 딕셔너리를 넣는다
                continue  # 더안내려가고 다시 for문으로 돌아감
            temp['coords'] = self.move_const(temp)  # 아래에 있는 함수에서 리턴받은 s_(삼격형이 움직이고 난 픽셀좌표)를 coords에 넣어준다. 
            temp['state'] = self.coords_to_state(temp['coords'])  # 픽셀값을 x,y좌표로 state에 넣어준다.
            new_rewards.append(temp)  # 뉴리워드 리스트에 위에 변경된 값을 넣어주고
        return new_rewards  # 리턴

    def move_const(self, target):  # target은 위에서 temp 이고 // 위데 temp에는 세모 세개의 딕셔너리가 for문으로 하나씩 들어오게된다.

        s = self.canvas.coords(target['figure'])  # 타겟 figure는 값이 두개인데 s하나로 넣으면 리스트로 받음 s = [width, height]

        base_action = np.array([0, 0])

        if s[0] == (WIDTH - 1) * UNIT + UNIT / 2:  # 제일 마지막 그리드에 도착시에
            target['direction'] = 1  # 세모의 다이렉션은 1이된다. 아마 1은 왼쪽으로 움직이게 하는 무엇인가
        elif s[0] == UNIT / 2:  # 처음 칸에 오면 
            target['direction'] = -1  # 다이렉션은 -1이고 오른쪽으로 움직이게 된다.

        if target['direction'] == -1:  # 세모가 처음칸에 도착하면
            base_action[0] += UNIT  # 세모의 x픽셀좌표값에 픽셀값을 한번씩 더해준다.
        elif target['direction'] == 1: # 세모가 마지막칸에 도착하면
            base_action[0] -= UNIT  # 세모의 x픽셀좌표값에 픽셀값을 한번씩 빼준다.

#         if (target['figure'] is not self.rectangle  # 네모와 세모의 위치가 같지 않을때
#            and s == [(WIDTH - 1) * UNIT, (HEIGHT - 1) * UNIT]):  # 
#             base_action = np.array([0, 0])

        self.canvas.move(target['figure'], base_action[0], base_action[1])  # figure가 가지는 고유 숫자는 그대로 이고 고유숫자의 위치는 계속 바뀔수 있다. x,y와 각각픽셀값은 변할 수 있다.

        s_ = self.canvas.coords(target['figure'])  # 업뎃한 픽셀값들을 s_로 

        return s_

    def move(self, target, action):
        s = self.canvas.coords(target)  # 사각형이 타겟

        base_action = np.array([0, 0])

        if action == 0:  # 상  # 0이나와서 위로 움직여야할때
            if s[1] > UNIT:  # s1의 픽셀값이 50이면 올라갈수 없으므로 50보다 커야하고 크다면
                base_action[1] -= UNIT  # 50만큼 빼줘서 위로 올려준다.
        elif action == 1:  # 하
            if s[1] < (HEIGHT - 1) * UNIT:
                base_action[1] += UNIT
        elif action == 2:  # 우
            if s[0] < (WIDTH - 1) * UNIT:
                base_action[0] += UNIT
        elif action == 3:  # 좌
            if s[0] > UNIT:
                base_action[0] -= UNIT

        self.canvas.move(target, base_action[0], base_action[1])  # 바뀐 사각형의 좌표

        s_ = self.canvas.coords(target)  # 바뀐사각형의 좌표값을 픽셀값으로

        return s_  # s_을 반환

    def render(self):
        # 게임 속도 조정
        time.sleep(self.render_speed)
        self.update()
