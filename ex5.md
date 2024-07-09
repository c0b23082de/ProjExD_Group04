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

import os
import sys
import pygame as pg
import random


WIDTH, HEIGHT = 1000, 700
DELTA = {  # 移動量辞書
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect，または，爆弾Rect
    戻り値：真理値タプル（横方向，縦方向）
    画面内ならTrue／画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦方向判定
        tate = False
    return yoko, tate

# def muki():
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

