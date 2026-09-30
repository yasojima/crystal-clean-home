/**
 * 年越大そうじキャンペーンページ - JavaScript
 * クーポンコードコピー機能とインタラクション
 * (PC/SP対応・リファクタリング版)
 */

// ----------------------------------------
// メインのコピー関数（引数で受け取ったテキストをコピー）
// ----------------------------------------
function copyTextToClipboard(text) {
  // クリップボードAPIを使用してコピー
  if (navigator.clipboard && window.isSecureContext) {
    // モダンブラウザ向け
    navigator.clipboard.writeText(text).then(() => {
      showCopyNotification('クーポンコードをコピーしました');
    }).catch(err => {
      console.error('コピーに失敗しました:', err);
      fallbackCopyTextToClipboard(text);
    });
  } else {
    // 古いブラウザ向けのフォールバック
    fallbackCopyTextToClipboard(text);
  }
}

// ----------------------------------------
// フォールバック：古いブラウザでのコピー処理
// ----------------------------------------
function fallbackCopyTextToClipboard(text) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.top = '0';
  textArea.style.left = '0';
  textArea.style.width = '2em';
  textArea.style.height = '2em';
  textArea.style.padding = '0';
  textArea.style.border = 'none';
  textArea.style.outline = 'none';
  textArea.style.boxShadow = 'none';
  textArea.style.background = 'transparent';

  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    const successful = document.execCommand('copy');
    if (successful) {
      showCopyNotification('クーポンコードをコピーしました');
    } else {
      showCopyNotification('コピーに失敗しました', 'error');
    }
  } catch (err) {
    console.error('フォールバックコピーに失敗しました:', err);
    showCopyNotification('コピーに失敗しました', 'error');
  }

  document.body.removeChild(textArea);
}

// ----------------------------------------
// コピー完了通知（トースト）を表示する関数
// ----------------------------------------
function showCopyNotification(message, type = 'success') {
  // 既存の通知があれば削除
  const existingNotification = document.querySelector('.copy-notification');
  if (existingNotification) {
    existingNotification.remove();
  }

  // 通知要素を作成
  const notification = document.createElement('div');
  notification.className = `copy-notification ${type}`;
  notification.textContent = message;

  // スタイルを設定
  notification.style.position = 'fixed';
  notification.style.bottom = '50%';
  notification.style.left = '50%';
  notification.style.transform = 'translateX(-50%)';
  notification.style.backgroundColor = type === 'success' ? '#2977d6' : '#f44336';
  notification.style.color = '#fff';
  notification.style.padding = '15px 10px';
  notification.style.borderRadius = '8px';
  notification.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
  notification.style.fontSize = '16px';
  notification.style.fontWeight = 'bold';
  notification.style.zIndex = '9999';
  notification.style.animation = 'slideUp 0.3s ease';
  notification.style.maxWidth = '80%'; // 画面幅の8割まで
  notification.style.wordWrap = 'break-word'; // 長い文字列で折り返し
  notification.style.textAlign = 'center';

  // ページに追加
  document.body.appendChild(notification);

  // 3秒後に自動削除
  setTimeout(() => {
    notification.style.animation = 'slideDown 0.3s ease';
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3000);
}

// ----------------------------------------
// アニメーションのCSSを動的に追加
// ----------------------------------------
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateX(-50%) translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    }
    
    @keyframes slideDown {
        from {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
        to {
            opacity: 0;
            transform: translateX(-50%) translateY(20px);
        }
    }
`;
document.head.appendChild(style);

// ----------------------------------------
// ページの読み込み完了時にすべてのイベントを設定
// ----------------------------------------
document.addEventListener('DOMContentLoaded', () => {

  // --- 1. スムーススクロール機能（アンカーリンク用） ---
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');

      // "#"のみの場合はスクロールしない
      if (href === '#') {
        e.preventDefault();
        return;
      }

      const targetId = href.substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // --- 2. クーポンコード「テキスト」(#couponCode) のクリックイベント ---
  const couponCodeElement = document.getElementById('couponCode');
  if (couponCodeElement) {
    couponCodeElement.style.cursor = 'pointer';
    couponCodeElement.addEventListener('click', (e) => {
      e.preventDefault(); // リンクの動作をキャンセル
      const codeToCopy = couponCodeElement.textContent;
      copyTextToClipboard(codeToCopy);
    });
  }

  // --- 3. クーポンコード「画像」(.copy-coupon-trigger) のクリックイベント (PC/SP両対応) ---
  // クラス名を 'copy-coupon-trigger' に変更した場合
  const couponImages = document.querySelectorAll('.copy-coupon-trigger');
  if (couponImages.length > 0) {
    const codeToCopy = "m1025"; // 画像クリック時はこのコードをコピー

    couponImages.forEach(image => {
      image.addEventListener('click', (e) => {
        e.preventDefault(); // リンクの動作をキャンセル
        copyTextToClipboard(codeToCopy);
      });
    });
  }

  // コンソールログ（開発用）
  console.log('年越大そうじキャンペーンページが読み込まれました');
});