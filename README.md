# 生き残れこうかとん

## 実行環境の必要条件
* python >= 3.10
* pygame >= 2.1

## ゲームの概要
こうかとんに敵が襲いかかってくるのを倒してスコアを伸ばしていくゲーム

## ゲームの遊び方
* 矢印キーでこうかとんを操作し敵をよけながら倒していくゲーム
* こうかとんの上にHPバーがあり、全部なくなるとゲームオーバーとなる
  ボスを倒すとゲーム終了

## ゲームの実装
### 共通基本機能
* 背景と主人公キャラクターの描画
* 敵がプレイヤーに群がるように移動
* 討伐数に応じて徐々に敵を増やしていく
* プレイヤーにHPをつける

###追加機能
* スコアに応じて攻撃する技の種類が増えていく機能　担当:霜越 
スコアが50になると斜め上と斜め下にビームを追加
スコアが300になるとこうかとんの周りを回るシールドが出現し、当たると自動的に敵を倒す

* 敵ごとにそれぞれHPを付与する機能  担当:中島
敵が三種類おりランダムにそれぞれ１から３のHPが割り振られる
攻撃が当たるごとにHPが１ずつ減っていく

* ボスの登場  担当:吉樂
スコアが400を突破すると、画面右端からドッペルゲンガーが出現
ボスにも体力が設定されており、ボスを倒せばゲームクリア
ボスに当たってもダメージ判定はない(実装できなかった)

* 回復アイテムの追加  担当:藤塚
一定フレームごとに回復アイテムをフィールドに表示させる
アイテムに触れるとこうかとんのHPが１０回復する
### ToDo
[]  ビームが敵に当たっても消えずに貫通するビームをしたかった
-  HPの違う敵を1~3に分けてそれぞれ別の画像で表示させたかった

### ゲーム画面
<img width="817" alt="image" src="https://github.com/user-attachments/assets/9f2eac2a-47fe-46b9-919d-a60ab6a19d24">


