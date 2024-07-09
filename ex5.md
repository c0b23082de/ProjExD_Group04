# 丸焼き豪華豚

## 実行環境の必要条件
* python >= 3.10
* pygame >= 2.1

## ゲームの概要
主人公キャラクターに敵が襲いかかってくるのを倒してスコアを伸ばしていくゲーム

## ゲームの遊び方
* 矢印キーでこうかとんを操作し，スペースキー押下による攻撃
* ライフが三つあり全部なくなるとゲームオーバーとなる

## ゲームの実装
### 共通基本機能
*背景と主人公キャラクターの描画
*敵がプレイヤーに群がるように移動
*討伐数に応じて徐々に敵を増やしていく
*プレイヤーにHPをつける
import math
import os
import sys
import time
import pygame as pg
import random


WIDTH, HEIGHT = 1000, 700
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
    return x_diff/norm, y_diff/norm

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

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 2.0)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 900, 400
    bb_img = pg.Surface((20, 20))  # 1辺が20の空のSurfaceを作る
    bb_img.set_colorkey((0, 0, 0))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 空のSurfaceに赤い円を描く
    bb_rct = bb_img.get_rect()  # 爆弾Rect
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾の横方向速度，縦方向速度
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            
        if kk_rct.colliderect(bb_rct):  # 衝突判定
            a = pg.Surface((1000,700))
            pg.draw.rect(a,(0,0,0),pg.Rect(0,0,1000,700))
            a.set_alpha(100)
            screen.blit(a,[0,0])
            fonto = pg.font.Font(None, 80) 
            txt = fonto.render("Game Over", True, (255, 255, 255)) 
            screen.blit(txt, [350, 300])
            pg.display.update()
            clock.tick(0.5)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for k, v in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += v[0]
                sum_mv[1] += v[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)
        bb_rct.move_ip(vx, vy)   

        yoko, tate = check_bound(bb_rct)
        if not yoko: 
            vx *= -1
        if not tate: 
            vy *= -1   
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)
        # accs = [a for a in range(1, 11)]
        # for r in range(1, 11):
        #     bb_img = pg.Surface((20*r, 20*r))
        #     pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        #     avx = vx*bb_accs[min(tmr//500, 9)]
        #     bb_img = bb_imgs[min(tmr//500, 9)]
        # screen.blit(bb_img)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()




### 担当追加機能
* 敵を倒した数に応じて攻撃する技の種類が増えていく機能
* フィールド上のアイテムを拾うことでプレイヤーにイベントが起こる機能(例：HP回復、一時的に技が増える)
* 討伐数に応じてボスが出現する機能
* ポイントを消費して敵を一掃できる機能
* 
### ToDo


### メモ

