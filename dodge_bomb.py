import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0,-5),
    pg.K_DOWN: (0,+5),
    pg.K_LEFT: (-5,0),
    pg.K_RIGHT: (+5,0)
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct:pg.Rect) -> tuple[bool,bool]:
    """
    引数：こうかとんRect or ばくだんRect
    戻り値：タプル(横方向判定結果、縦方向判定結果)
    画面内ならTrue,画面外ならFalse
    """
    yoko,tate = True,True
    if rct.left < 0 or WIDTH < rct.right: #横方向にはみ出ていたら
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: #縦方向にはみ出ていたら
        tate = False
    return yoko,tate


def gameover(screen: pg.Surface) -> None: #ゲームオーバー画面
    black = pg.Surface((WIDTH,HEIGHT)) #1 黒い矩形Surfaceを作成
    black.fill((0,0,0))
    black.set_alpha(200) #2 黒い矩形を半透明
    fonto = pg.font.Font(None, 120)
    txt = fonto.render("Game Over", True, (255, 255, 255)) #Game Over文字出力
    txt_rct = txt.get_rect(center=(WIDTH//2, HEIGHT//2))
    k2_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.0) #3 泣いているこうかとん画像読み込み
    k2_rct = k2_img.get_rect(center=(WIDTH//2+300, HEIGHT//2 )) #右こうかとん
    k2_rct2 = k2_img.get_rect(center=(WIDTH//2-300, HEIGHT//2 )) #左こうかとん
    screen.blit(black, (0, 0)) #4 Surfaceを重ねて描画
    screen.blit(txt, txt_rct)
    screen.blit(k2_img, k2_rct)
    screen.blit(k2_img, k2_rct2)
    pg.display.update() 
    time.sleep(5) #5 画面更新後5秒停止

def init_bb_imgs() -> tuple[list[pg.Surface],list[int]]: #時間とともに爆弾が拡大、加速する
    bb_imgs = [] #爆弾を定義
    for r in range(1,11):
        bb_img = pg.Surface((20*r,20*r))
        pg.draw.circle(bb_img,(255,0,0),(10*r,10*r),10*r)
        bb_img.set_colorkey((0,0,0))
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1,11)]
    return bb_imgs,bb_accs


def get_kk_imgs(kk_img: pg.Surface) -> dict[tuple[int, int], pg.Surface]: #3飛ぶ方向に従って効果トン画像を切り替える
    kk_imgs = {}
    for dx, dy in [
        (0, 0), (0, -5), (0, +5), (-5, 0), (+5, 0),
        (-5, -5), (-5, +5), (+5, -5), (+5, +5)
    ]:
        if dx == 0 and dy == 0:
            kk_imgs[(dx, dy)] = kk_img 
        else:
            angle = {
                (0, -5): 90,
                (0, +5): 270,
                (-5, 0): 180,
                (+5, 0): 0,
                (-5, -5): 135,
                (-5, +5): 225,
                (+5, -5): 45,
                (+5, +5): 315
            }[(dx, dy)]
            kk_imgs[(dx, dy)] = pg.transform.rotozoom(kk_img, angle, 1.0)
    return kk_imgs


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20,20)) #空のSurface
    pg.draw.circle(bb_img,(250,0,0),(10,10),10) #赤い爆弾円
    bb_img.set_colorkey((0,0,0))#四隅の黒い部分を透過
    bb_rct = kk_img.get_rect() #爆弾
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0,HEIGHT)
    bb_imgs,bb_accs = init_bb_imgs() 
    vx,vy = +5,+5
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 
        if kk_rct.colliderect(bb_rct): #こうかとん爆弾の衝突判定
            gameover(screen) #ゲームオーバー
            return 
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0] #横方向の移動量を加算
                sum_mv[1] += mv[1] #縦方向の移動量を加算
        #if key_lst[pg.K_UP]:
            #sum_mv[1] -= 5
        #if key_lst[pg.K_DOWN]:
            #sum_mv[1] += 5
        #if key_lst[pg.K_LEFT]:
            #sum_mv[0] -= 5
        #if key_lst[pg.K_RIGHT]:
            #sum_mv[0] += 5
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True,True):
            kk_rct.move_ip(-sum_mv[0],-sum_mv[1])
        screen.blit(kk_img, kk_rct)
        avx = vx*bb_accs[min(tmr//500, 9)]
        avy = vy*bb_accs[min(tmr//500, 9)]
        bb_img = bb_imgs[min(tmr//500, 9)]
        bb_rct.move_ip(avx,avy) #爆弾移動
        yoko,tate = check_bound(bb_rct)
        if not yoko: #横方向にはみでていたら
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img, bb_rct) #爆弾描画
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
