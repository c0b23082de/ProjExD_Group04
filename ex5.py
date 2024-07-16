import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    try:
        return x_diff/norm, y_diff/norm
    except ZeroDivisionError:
        return 0, 0

def draw_hp_bar(surface,x,y,k_hp:int,k_max_hp:int):
    """
    こうかとんのHPバーを表示
    引数1 surface: screan
    引数2 x: HPバーのx座標
    引数3 y: HPバーのy座標
    引数4 k_hp:こうかとんの今のHP
    引数5 k_max_hp こうかとんの最大HP 
    """

    hp_bar_wdith = 150
    hp_bar_height = 20 
    #HPの割合を計算
    hp_ratio = k_hp / k_max_hp

    #バー外枠を描画
    pg.draw.rect(surface,(255,0,0),(x,y,hp_bar_wdith,hp_bar_height))

    #HPバーの中身を描画
    fill_width = int(hp_bar_wdith * hp_ratio)
    pg.draw.rect(surface,(0,255,0),(x,y,fill_width,hp_bar_height))

class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        if key_lst[pg.K_LSHIFT]:
            self.speed = 20
        else:
            self.speed = 10
        screen.blit(self.image, self.rect)


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird, angle0=0):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx)) + angle0
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10


    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()
    

class NeoBeam:
    """
    ビームを複数打てるかもしれないクラス
    """
    def __init__(self, bird: Bird, num: int):
        self.bird = bird
        self.num = num
    def gen_beams(self):
        """
        引数 num：ビームの本数
        """
        return [Beam(self.bird, angle) for angle in range(-50, 51, int(100/(self.num-1)))]

class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()

class Gravity(pg.sprite.Sprite):
    def __init__(self,life:int):
        super().__init__()

        self.image = pg.Surface((WIDTH,HEIGHT))
        self.life = life
        pg.draw.rect(self.image,(0,0,0),pg.Rect(0,0,WIDTH,HEIGHT))
        self.rect = self.image.get_rect()
        self.image.set_alpha(180)

    def update(self):
        self.life -= 1
        if self.life < 0:
            self.kill()

# class newbeam(pg.sprite.Sprite):
#     def __init__(self, bird: Bird, num: int):
#         self.bird = bird
#         self.num = num
#     def gen_beams(self):
#         """
#         引数 num：ビームの本数
#         """
#         return [Beam(self.bird, angle) for angle in range(-50, 51, int(100/(self.num-1)))]

class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    
    def __init__(self, bird:Bird):
        smplace = [(random.randint(0, WIDTH), 0), 
                   (random.randint(0, WIDTH), HEIGHT), 
                   (0, random.randint(0, HEIGHT)), 
                   (WIDTH, random.randint(0, HEIGHT))]
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = smplace[random.randint(0,3)]
        self.vx, self.vy = calc_orientation(self.rect, bird.rect)  
        self.speed = 2
        self.rect.centerx = self.rect.centerx
        self.rect.centery = self.rect.centery+self.rect.height//2

    def update(self, bird:Bird):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        self.vx, self.vy = calc_orientation(self.rect, bird.rect) 
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
    

class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)

class Shield(pg.sprite.Sprite):
    """
    キャラクターの周りを周回して敵を倒すクラス
    """
    def __init__(self, bird: Bird):
        super().__init__()
        original_image = pg.image.load(f"fig/orbit.png")
        self.image = pg.transform.scale(original_image, (original_image.get_width() // 2,
        original_image.get_height() // 2))#画像サイズを半分にする
        self.rect = self.image.get_rect()
        self.bird = bird
        self.angle = 0  # 旋回角度の初期値
        self.radius = 100  # キャラクターからの距離

    def update(self):
        """
        キャラクターの周りを周回するように位置を更新する
        """
        self.angle += 3  # 角度を増加させて旋回させる
        rad_angle = math.radians(self.angle)
        self.rect.centerx = self.bird.rect.centerx + self.radius * math.cos(rad_angle)
        self.rect.centery = self.bird.rect.centery + self.radius * math.sin(rad_angle)



def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    score = Score()

    bird = Bird(3, (600, 500))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    grav = pg.sprite.Group()
    shields = pg.sprite.Group()
    shield_added = False
    k_max_hp = 5
    k_hp = k_max_hp
    tmr = 0
    clock = pg.time.Clock()
    flag = 1.0
    framer = 20
    
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if  key_lst[pg.K_RETURN] and score.value >= 200:
                    grav.add(Gravity(400))
                    score.value -= 200
  
        screen.blit(bg_img, [0, 0])

    
        a = score.value
        if a/100 == flag: # スコアが100の倍数ごとにframerを値を減る
            flag+=1       # 値が減るごとに来る敵の数が増えていく
            framer -= 1
        if framer <= 0:
            framer = 1
        print(framer)

        if tmr%framer == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy(bird))

        if tmr%30 == 0:  # 300フレームに1回，ビームを出現させる
            beams.add(Beam(bird))
    
        # スコアが50を超えた場合にビームを追加
        if score.value >= 50:
            if tmr % 50 == 0:
                beams.add(Beam(bird, -45))  # 左上方向にビームを追加
                beams.add(Beam(bird, 45))   # 右下方向にビームを追加
    
        # スコアが300を超えた場合にシールドを追加
        if score.value >= 300 and not shield_added:
            shields.add(Shield(bird))
            shield_added = True
        


        # for emy in emys:
        #     if emy.state == "stop" and tmr%emy.interval == 0:
        #         # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
        #         bombs.add(Bomb(emy, bird))

        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
 

        for bomb in pg.sprite.groupcollide(bombs, grav, True, False).keys():
            exps.add(Explosion(bomb,50))

        for emy in pg.sprite.groupcollide(emys, grav, True, False).keys():
            exps.add(Explosion(emy,100))

        for emy in pg.sprite.groupcollide(emys, shields, True, False).keys():
            exps.add(Explosion(emy, 100))  # シールドに当たった敵機は倒される

        draw_hp_bar(screen,bird.rect.centerx - 75,bird.rect.centery - 65,k_hp,k_max_hp)
        if len(pg.sprite.spritecollide(bird, emys, True)) != 0:
            k_hp -= 1
        if k_hp < 0:
            bird.change_img(8, screen) # こうかとん悲しみエフェクト
            score.update(screen)
            pg.display.update()
            time.sleep(2)
            return
        


        grav.update()
        grav.draw(screen)
        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update(bird)
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        shields.update()
        shields.draw(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
