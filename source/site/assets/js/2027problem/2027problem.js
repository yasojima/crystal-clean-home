// JavaScript Document
// 設定はここから -----------------
/*
質問
[見出し, 質問内容, 注釈, はいのスコア]
*/
const question = [
  // 質問1
  [
    "Q1.",
    "今使っているエアコンの<br>使用年数は10年以上",
    "エアコンの標準使用期間を10年と設定しているメーカーもあります。15年以上経過している場合は不具合が出ていなくても標準使用期間を超えているので買い替えを検討するタイミングとなります。",
    3
  ],
  // 質問2
  [
    "Q2.",
    "最近効きが悪くなった",
    "エアコンの効きが悪くなる原因として内部に蓄積された汚れの可能性があり、その場合プロの分解洗浄で解決できる可能性があります。",
    1
  ],
  // 質問3
  [
    "Q3.",
    "エアコンから異臭がする<br>ときがある（特に夏場）",
    "エアコンの異臭は、内部の汚れによるカビや雑菌の繁殖が原因の場合があり、分解洗浄で解決できる可能性があります。",
    1
  ],
  // 質問4
  [
    "Q4.",
    "エアコンから異音がする。<br>またはエラーコードが出ている",
    "エラーコードはWEBや取扱説明書で確認いただけます。モーターや室外機など稼働に大きな支障が出るような不具合の場合は分解洗浄では復帰せず修理が必要な場合もあります。",
    2
  ],
  // 質問5
  [
    "Q5.",
    "電気代が気になりますか？",
    "エアコンの室外機や室内機を分解洗浄して汚れを取り除くことでエアコンの稼働効率が向上して節電につながる可能性もあります。",
    1
  ],
];

/*
結果ルール
start: この表示コメントの開始スコア、スコアは昇順になるように設定
comment: 表示コメントの内容
*/
const resultRule = [
  { start: 0, comment: "今すぐ買い替える必要はなさそう。年に一回はプロの分解洗浄で汚れをリセットすることをおススメ。" },
  { start: 3, comment: "買い替える必要はなさそうですが、まずはプロの分解洗浄で汚れをリセット。洗浄～作動確認で不具合がないか点検もしてもらう。" },
  { start: 5, comment: "買い替えの検討が必要な可能性がありますが、まずはプロに分解洗浄を依頼して、汚れの状況や作動確認をしてもらう。" },
  { start: 7, comment: "具体的に買い替えを検討すべき状況。" },
];
// 設定はここまで -----------------------------------------------

// 質問から最大スコアを自動計算
const maxScore = question.reduce((total, item) => total + item[3], 0);

// 初期値
let index = 0;
let score = 0;

// DOM
const debugCount = document.getElementById("debugCount"); // 動作チェック
const startArea = document.getElementById("startArea");
const startBtn = document.getElementById("startBtn");
const questionArea = document.getElementById("questionArea");
const qHeading = document.getElementById("qHeading");
const qText = document.getElementById("qText");
const qAnnotation = document.querySelector("#qAnnotation small");
const yesBtn = document.getElementById("yesBtn");
const noBtn = document.getElementById("noBtn");
const resultArea = document.getElementById("resultArea");
const resultHeading = document.getElementById("resultHeading");
const resultText = document.getElementById("resultText");

// 動作チェック：カウント数出力
function updateDebugCount() {
  debugCount.textContent = "集計結果：" + score;
}

// 質問出力
function showQuestion() {
  qHeading.textContent = question[index][0];
  qText.innerHTML = question[index][1];
  qAnnotation.textContent = question[index][2];

  // 既存のquestion系クラスだけ削除
  [...questionArea.classList].forEach(cls => {
    if (cls.startsWith("question")) {
      questionArea.classList.remove(cls);
    }
  });

  // 新しいクラス追加
  questionArea.classList.add("question" + (index + 1));
}

// スタート画面から質問画面に切り換え
startBtn.addEventListener("click", () => {
  startArea.style.display = "none";
  questionArea.style.display = "block";
  showQuestion();
  updateDebugCount();
});

// はい
yesBtn.addEventListener("click", () => {
  score += question[index][3];
  updateDebugCount();
  next();
});

// いいえ
noBtn.addEventListener("click", () => {
  next();
});

// 次の質問に切り換え
function next() {
  index++;

  if (index < question.length) {
    showQuestion();
  } else {
    showResult();
  }
}

// 現在のスコアに一致する結果ルールを取得
function getResultData(currentScore) {
  for (let i = 0; i < resultRule.length; i++) {
    const start = resultRule[i].start;
    const nextRule = resultRule[i + 1];
    const end = nextRule ? nextRule.start - 1 : maxScore;

    if (currentScore >= start && currentScore <= end) {
      return {
        type: i,
        start: start,
        end: end,
        comment: resultRule[i].comment
      };
    }
  }

  /*
  万が一の保険
  下記ゲースがあるとエラーになるため、最低でもタイプ0として表示
  ケース1：配列resultRuleのstartが昇順になっていない場合
  ケース2：変数scoreの値がNaN、負の整数の場合
  */
  return {
    type: 0,
    start: 0,
    end: maxScore,
    comment: resultRule[0].comment
  };
}

// 結果表示
function showResult() {
  questionArea.style.display = "none";
  resultArea.style.display = "block";

  const resultData = getResultData(score);
  const rangeText = `${resultData.start}〜${resultData.end}`;

  resultHeading.textContent = "" + rangeText;
  resultText.textContent = resultData.comment;
}

// 動作チェック：カウント数出力の実行
 updateDebugCount();


//スタート画面に戻る
const returnBtn = document.getElementById("returnBtn");

returnBtn.addEventListener("click", () => {
  // 状態リセット
  index = 0;
  score = 0;

  // 表示切り替え
  resultArea.style.display = "none";
  questionArea.style.display = "none";
  startArea.style.display = "block";

  // 念のため更新
  updateDebugCount();
});