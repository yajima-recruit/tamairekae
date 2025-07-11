import pygame
import random

# === クラス定義 ===

# ボタンクラス（anchor対応）
class Button:
    def __init__(self, size, text, anchor="topleft", pos=(0, 0), font=None, base_color=(180, 180, 180), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect((0, 0), size)
        setattr(self.rect, anchor, pos)

        self.text = text
        self.font = font or pygame.font.Font(None, 36)
        self.base_color = base_color
        self.hover_color = hover_color
        self.is_pressed = False

    def set_position(self, anchor="topleft", pos=(0, 0)):
        """任意の位置・基点(anchor)に再配置"""
        setattr(self.rect, anchor, pos)

    def draw(self, screen):
        color = self.hover_color if self.is_hovered() else self.base_color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=10)

        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def update(self, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered():
                self.is_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_pressed and self.is_hovered():
                    self.is_pressed = False
                    return True
                self.is_pressed = False
        return False

# === 関数定義 ===

# ステージをリサイズする
def resize_stage(screen_width, screen_height, circle_num, lane_num):
    global box
    # 縦を基準として計算
    stage_height = screen_height * 0.8 - button_height
    box = int(stage_height / circle_num)
    stage_width = box * lane_num

    # ステージの横の長さがウィンドウの横の長さの8割りより大きかった場合、ウィンドウの横を基準としてステージを再計算
    if stage_width > screen_width * 0.95:
        stage_width = screen_width * 0.8
        box = int(stage_width / lane_num)
        stage_height = box * circle_num
    stage = pygame.Rect(0, 0, stage_width, stage_height)  # (x, y, 幅, 高さ)
    stage.center = (screen_width / 2, screen_height / 2 - button_height)

    hidden_stage = []
    base_x, base_y = stage.topleft
    for i in range(lane_num):
        hidden_stage.append(pygame.Rect(base_x + i * box, base_y, box, stage_height))
    
    return stage, hidden_stage

# 2次元配列の中身をシャッフルする
def shuffle_2d_array(array):
    flat = [item for row in array for item in row]
    random.shuffle(flat)
    rows = len(array)
    cols = len(array[0]) if rows > 0 else 0
    return [flat[i * cols:(i + 1) * cols] for i in range(rows)]

# 配列の中を整理する
def aline_array(array):
    result = []
    for row in array:
        # None を取り出して先に、残りの値を後ろに
        new_row = [item for item in row if item is not None] + [item for item in row if item is None]
        result.append(new_row)
    return result

# 円の位置と大きさを指定する
def calculate_circle_position():
    base_x, base_y = stage.bottomleft
    circle_base = (box - line_width) / 2
    for y in range(len(stage_data)):
        work_y = base_y
        for x in range(len(stage_data[y])):
            if stage_data[y][x] == None:
                continue
            stage_data[y][x]['center'] = (
                base_x + box * y + (box + line_width) / 2,
                work_y - circle_base
            )
            stage_data[y][x]['radius'] = circle_base
            work_y -= circle_base * 2
    return stage_data

# 玉を移動させる
def move_circle(i):
    swap_circle = pop_rightmost_non_none(stage_data[lifting['lane']])
    # 移動先の配列に玉情報を移動
    move_data(stage_data[i], swap_circle)
    calculate_circle_position()

    # 持ち上げ情報をリセットする
    lifting["direction"] = 0
    lifting["lane"] = None
    lifting["circle"] = None

# 配列を右から検索しNone以外の最初の要素を取得しその位置をNoneに変える
def pop_rightmost_non_none(array):
    for i in range(len(array) - 1, -1, -1):
        if array[i] is not None:
            value = array[i]
            array[i] = None
            return value
    return None  # 全部 None だった場合

# 移動先に玉情報を入れる
def move_data(array, info):
    for i in range(len(array)):
        if array[i] == None:
            array[i] = info
            break

# クリアチェック
def clear_check():
    for circles in stage_data:
        hold = circles[0]["color"] if circles[0] is not None else None
        for circle in circles:
            work =  circle["color"] if circle is not None else None
            if hold != work:
                return False
    return True

# === シーンごとのイベント処理関数 ===
def scene_title_event(events):
    global screen, scene_counter, difficulty
    for event in events:
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            # ボタンの位置調整
            button_array[0].set_position(anchor="center", pos=(screen.get_width() / 2 - 210,    int(screen.get_height() * 0.55)))
            button_array[1].set_position(anchor="center", pos=(screen.get_width() / 2,          int(screen.get_height() * 0.55)))
            button_array[2].set_position(anchor="center", pos=(screen.get_width() / 2 + 210,    int(screen.get_height() * 0.55)))
            button_array[3].set_position(anchor="center", pos=(screen.get_width() / 2,          int(screen.get_height() * 0.7)))

    # ボタンが押されたかどうか
    if button_array[0].update(events):
        difficulty = "かんたん"
    if button_array[1].update(events):
        difficulty = "ふつう"
    if button_array[2].update(events):
        difficulty = "むずかしい"
    if button_array[3].update(events):
        scene_counter = "game"

def scene_game_event(events):
    global screen, stage, hidden_stage, stage_data, lifting, clear_flag, scene_counter, previous_scene
    # イベント取得
    for event in events:
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            width, height = event.size
            
            # ステージを再定義
            stage, hidden_stage = resize_stage(width, height, circle_num, lane_num)

            # 円を再定義
            stage_data = calculate_circle_position()

            # ボタンの位置調整
            button_array[0].set_position(anchor="center", pos=(screen.get_width() / 2 - 150, (screen.get_height() + stage.bottom) / 2))
            button_array[1].set_position(anchor="center", pos=(screen.get_width() / 2 + 150, (screen.get_height() + stage.bottom) / 2))

            # 円が持ち上げられている場合調整
            if lifting["lane"] != None:
                for row in reversed(stage_data[lifting["lane"]]):
                    if row is not None:
                        lifting["target_y"] = row["center"][1] - 20
                        lifting["direction"] = -1
                        break
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(hidden_stage)):
                if hidden_stage[i].collidepoint(event.pos):
                    for row in reversed(stage_data[i]):
                        if row is not None:

                            # 何も持ち上がっていない
                            if lifting["lane"] == None:
                                # 持ち上げる
                                lifting["target_y"] = row["center"][1] - 20
                                lifting["direction"] = -1
                                lifting["lane"] = i
                                lifting["circle"] = row
                            
                            # すでに上がっていて同じレーンをクリックした場合
                            elif lifting["lane"] == i:
                                # 元に戻す
                                lifting["target_y"] = row["center"][1] + 20
                                lifting["direction"] = 1
                                lifting["lane"] = None
                                lifting["circle"] = row

                            # 別レーンをクリックして移動先の配列に空きがあるか確認
                            elif None in stage_data[i]:
                                # 対象のレーンに移動させる
                                move_circle(i)

                                # クリア判定
                                clear_flag = clear_check()
                                
                            break
                    else:
                        # 空のレーンへ移動させる場合
                        if lifting["lane"] != None:
                            # 対象のレーンに移動させる
                            move_circle(i)

                            # クリア判定
                            clear_flag = clear_check()

    # ボタンが押されたかどうか
    if button_array[0].update(events):
        scene_counter = "title"
    if button_array[1].update(events):
        previous_scene = None

def scene_end_event(events):
    global screen, scene_counter
    for event in events:
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            # ボタンの位置調整
            button_array[0].set_position(anchor="center", pos=(screen.get_width() / 2 - 150, int(screen.get_height() * 0.5)))
            button_array[1].set_position(anchor="center", pos=(screen.get_width() / 2 + 150, int(screen.get_height() * 0.5)))
    
    # ボタンが押されたかどうか
    if button_array[0].update(events):
        scene_counter = "title"
    if button_array[1].update(events):
        scene_counter = "game"

# === シーン変更後に1度だけ呼び出される処理 ===
def on_enter_title():
    global button_array

    # ボタンを作る
    button1 = Button((200, button_height), "かんたん", anchor="center", pos=(screen.get_width() / 2 - 210, int(screen.get_height() * 0.55)), font=pygame.font.Font(jp_font_path, 30))
    button2 = Button((200, button_height), "ふつう", anchor="center", pos=(screen.get_width() / 2, int(screen.get_height() * 0.55)), font=pygame.font.Font(jp_font_path, 30))
    button3 = Button((200, button_height), "むずかしい", anchor="center", pos=(screen.get_width() / 2 + 210, int(screen.get_height() * 0.55)), font=pygame.font.Font(jp_font_path, 30))
    button4 = Button((200, button_height), "ゲーム開始", anchor="center", pos=(screen.get_width() / 2, int(screen.get_height() * 0.7)), font=pygame.font.Font(jp_font_path, 30))
    # ボタン配列に保存
    button_array = [button1, button2, button3, button4]

def on_enter_game():
    global box, circle_num, lane_num, swap_circle, clear_flag, animations, animation_speed, animation_distance, lifting, stage, hidden_stage, stage_data, button_array
    box = 0
    width, height = screen.get_size() # 初期サイズ

    # 難易度によって個数を変える
    if difficulty == "かんたん":
        circle_num = random.randint(3,6) # 1列の丸の数
        lane_num = random.randint(3,5) # 列の数
    if difficulty == "ふつう":
        circle_num = random.randint(5,9)
        lane_num = random.randint(6,8)
    if difficulty == "むずかしい":
        circle_num = random.randint(7,11)
        lane_num = random.randint(9,11)
    
    swap_circle = None # 玉を入れ替えるための作業領域
    clear_flag = False # クリアフラグ

    # アニメーション中の玉を管理する（辞書: {"circle": 円データ, "dy": 残り移動量}）
    animations = []
    animation_speed = 3  # 1フレームごとに動かす距離（ピクセル）
    animation_distance = 30  # 動かす合計距離
    lifting = {
        "lane": None,     # 何番目のレーンか
        "circle": None,   # 玉オブジェクトへの参照
        "target_y": 0,    # 目標のY座標
        "direction": 0    # 上げるなら -1、下げるなら +1
    }

    # 土台の長方形
    stage, hidden_stage = resize_stage(width, height, circle_num, lane_num)

    # 色を選ぶ
    selected_colors = random.sample(colors, lane_num - 1)

    # ステージの配列を作る
    stage_data = [[{"color": selected_colors[i], "center": (0, 0), "radius": 1} for _ in range(circle_num)] for i in range(lane_num - 1)]
    stage_data.append([None for _ in range(circle_num)])

    # ステージの中身をシャッフルする
    stage_data = shuffle_2d_array(stage_data)

    # ステージの中身を整理する
    stage_data = aline_array(stage_data)

    # 円の座標を計算する
    stage_data = calculate_circle_position()

    # ボタン用フォント
    button_font = pygame.font.Font(jp_font_path, 30)
    # ボタンを作る
    button1 = Button((250, button_height), "タイトルへ戻る", anchor="center", pos=(screen.get_width() / 2 - 150, (screen.get_height() + stage.bottom) / 2), font=button_font)
    button2 = Button((250, button_height), "再生成", anchor="center", pos=(screen.get_width() / 2 + 150, (screen.get_height() + stage.bottom) / 2), font=button_font)
    # ボタン配列に保存
    button_array = [button1, button2]

def on_enter_end():
    global title_font, button_array
    # フォントを設定
    title_font = pygame.font.Font(jp_font_path, 40)
    button_font = pygame.font.Font(jp_font_path, 30)

    # ボタンを作る
    button1 = Button((250, button_height), "タイトルへ戻る", anchor="center", pos=(screen.get_width() / 2 - 150, int(screen.get_height() * 0.5)), font=button_font)
    button2 = Button((250, button_height), "もう一度やる",  anchor="center", pos=(screen.get_width() / 2 + 150, int(screen.get_height() * 0.5)), font=button_font)
    # ボタン配列に保存
    button_array = [button1, button2]

# === 各シーンの画面処理 ===
def scene_title_process():
    global scene_counter
    # テキストの表示を一括定義
    text_array = [
        pygame.font.Font(jp_font_path, 50).render("玉入れ替えパズル", True, (0, 0, 0)),
        pygame.font.Font(jp_font_path, 30).render(f"難易度：{difficulty}", True, (0, 0, 0))
    ]
    
    # テキストの表示位置を一括定義
    text_pos = [
        (screen.get_width() / 2, int(screen.get_height() * 0.3)),
        (screen.get_width() / 2, int(screen.get_height() * 0.4))
    ]

    # テキストを表示
    for i in range(len(text_array)):
        text_rect = text_array[i].get_rect(center=text_pos[i])
        screen.blit(text_array[i], text_rect)
    
    # ボタンの表示
    for i in range(len(button_array)):
        button_array[i].draw(screen)

def scene_game_process():
    global scene_counter
    # 土台を描画
    pygame.draw.rect(screen, stage_color, stage)

    # レーンの区切り線
    lane_width = stage.width / lane_num
    for i in range(0, lane_num + 1):
        x = stage.left + i * lane_width
        pygame.draw.line(screen, line_color, (x, stage.top), (x, stage.bottom), line_width)
    pygame.draw.line(screen, line_color, (stage.left, stage.bottom), (stage.right, stage.bottom), line_width)
    
    # 円を描画する
    for circles in stage_data:
        for circle in circles:
            if circle == None:
                continue
            pygame.draw.circle(screen, circle["color"], circle["center"], circle["radius"])
    
    # ボタンの表示
    for i in range(len(button_array)):
        button_array[i].draw(screen)

    # アニメーション処理
    if lifting["circle"]:
        x, y = lifting["circle"]["center"]
        target_y = lifting["target_y"]
        speed = 2  # 1フレームで動く量（小さくするとゆっくり）

        if (lifting["direction"] < 0 and y > target_y) or (lifting["direction"] > 0 and y < target_y):
            lifting["circle"]["center"] = (x, y + lifting["direction"] * speed)
        else:
            # 目標に到達
            lifting["circle"]["center"] = (x, target_y)
            lifting["direction"] = 0

    # クリアしたかどうか
    if clear_flag:
        scene_counter = "end"

def scene_end_process():
    global scene_counter
    # 文字列を描画
    title_text = title_font.render("クリアおめでとう！！", True, (0, 0, 0))
    # 画面の幅の中央に配置 画面の縦10%の位置に配置
    text_rect = title_text.get_rect(center=(screen.get_width() / 2, int(screen.get_height() * 0.3)))
    # テキストを表示
    screen.blit(title_text, text_rect)
    # ボタンの表示
    for i in range(len(button_array)):
        button_array[i].draw(screen)

# === 初期設定 ===

pygame.init()
screen = pygame.display.set_mode((1000, 800), pygame.RESIZABLE)
pygame.display.set_caption("玉入れ替えパズル")
clock = pygame.time.Clock()

# 変数定義
scene_counter = "title" # 表示するシーンを管理する変数
previous_scene = "title" # シーンの変化を見る変数
line_width = 3 # 線の太さ
jp_font_path = pygame.font.match_font("msgothic")  # または "meiryo"
button_height = 60 # ボタンの高さを一括管理
difficulty = "かんたん" # 難易度設定

# テキストを管理する変数を定義
text_array = []

# ボタンを管理する配列を定義
button_array = []

# 色を定義
colors = [
    pygame.Color("red"),
    pygame.Color("green"),
    pygame.Color("blue"),
    pygame.Color("yellow"),
    pygame.Color("orange"),
    pygame.Color("purple"),
    pygame.Color("pink"),
    pygame.Color("cyan"),
    pygame.Color("magenta"),
    pygame.Color("brown"),
]
stage_color = pygame.Color("gray")
line_color = pygame.Color("black")

# タイトルの初期設定を呼び出す 安全のために
on_enter_title()

running = True
while running:
    # ウィンドウを白に初期化
    screen.fill(pygame.Color("white"))

    # イベント取得
    events = pygame.event.get()

    # 全シーン共通イベント処理
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    
    # 各シーンイベント処理
    if scene_counter == "title":
        scene_title_event(events)
    elif scene_counter == "game":
        scene_game_event(events)
    elif scene_counter == "end":
        scene_end_event(events)

    # シーン変更検出（1度だけ実行）
    if scene_counter != previous_scene:
        if scene_counter == "title":
            on_enter_title()
        elif scene_counter == "game":
            on_enter_game()
        elif scene_counter == "end":
            on_enter_end()
        previous_scene = scene_counter

    # 各シーン画面処理
    if scene_counter == "title":
        scene_title_process()
    elif scene_counter == "game":
        scene_game_process()
    elif scene_counter == "end":
        scene_end_process()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
