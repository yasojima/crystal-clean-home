import { bindTranslationLayout } from "./shared-translation-layout.js";

export const translationSettings = Object.freeze({
      kind: "embedded-service",
      provider: "Google Translate",
      scriptSrc: "https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit",
      fallbackScriptSrc: "https://translate.googleapis.com/translate_a/element.js?cb=googleTranslateElementInit",
      includedLanguages: "af,sq,am,ar,hy,az,eu,be,bn,bs,bg,ca,ceb,zh-CN,zh-TW,co,hr,cs,da,nl,en,eo,et,fi,fr,fy,gl,ka,de,el,gu,ht,ha,haw,he,hi,hmn,hu,is,ig,id,ga,it,ja,jv,kn,kk,km,rw,ko,ku,ky,lo,la,lv,lt,lb,mk,mg,ms,ml,mt,mi,mr,mn,my,ne,no,ny,or,ps,fa,pl,pt,pa,ro,ru,sm,gd,sr,st,sn,sd,si,sk,sl,so,es,su,sw,sv,tl,tg,ta,tt,te,th,tr,tk,uk,ur,ug,uz,vi,cy,xh,yi,yo,zu",
});

let activeTranslateTargetId = "google-translate-footer-1";
let googleTranslateGadget = null;
let mountingTarget = null;
let readinessObserver = null;
let loadTimer = null;
const translationStorageKey = "crystal-clean-home-translation-language";

export function storedTranslationLanguage() {
  try { return sessionStorage.getItem(translationStorageKey) || ""; }
  catch { return ""; }
}

function rememberTranslationLanguage(language) {
  try {
    if (!language || language === "ja") sessionStorage.removeItem(translationStorageKey);
    else sessionStorage.setItem(translationStorageKey, language);
  } catch { /* Storage is optional for translating the current document. */ }
}
window.addEventListener("crystal-translation-restored", () => rememberTranslationLanguage(""));

function activeTarget() {
  return document.getElementById(activeTranslateTargetId) || document.querySelector("[data-google-translate]");
}

function clearReadinessWait() {
  clearTimeout(loadTimer);
  loadTimer = null;
  readinessObserver?.disconnect();
  readinessObserver = null;
}

function showLoadFailure() {
  clearReadinessWait();
  if (!window.google?.translate?.TranslateElement) document.getElementById("google-translate-script")?.remove();
  mountingTarget = null;
  googleTranslateGadget?.remove();
  googleTranslateGadget = null;
  const target = activeTarget();
  if (!target) return;
  target.replaceChildren();
  const message = document.createElement("p");
  message.textContent = "翻訳機能を読み込めませんでした。";
  const retry = document.createElement("button");
  retry.type = "button";
  retry.className = "translation-retry";
  retry.textContent = "もう一度読み込む";
  retry.addEventListener("click", ensureGoogleTranslate);
  target.append(message, retry);
}

function connectGoogleTranslateCombo() {
  const combo = googleTranslateGadget?.querySelector(".goog-te-combo");
  // The select is inserted before its language options arrive.
  if (!combo || combo.options.length < 2) return false;
  clearReadinessWait();
  mountingTarget = null;
  if (combo.dataset.crystalBound !== "true") {
    combo.dataset.crystalBound = "true";
    combo.addEventListener("change", () => rememberTranslationLanguage(combo.value));
    const storedLanguage = storedTranslationLanguage();
    if (storedLanguage && [...combo.options].some(option => option.value === storedLanguage) && combo.value !== storedLanguage) {
      combo.value = storedLanguage;
      combo.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }
  return true;
}

export function mountGoogleTranslateWidgets() {
  if (!window.google?.translate?.TranslateElement) return;
  const target = activeTarget();
  if (!target) return;
  if (googleTranslateGadget && !googleTranslateGadget.isConnected) googleTranslateGadget = null;
  if (googleTranslateGadget) {
    if (googleTranslateGadget.parentElement !== target) target.replaceChildren(googleTranslateGadget);
    connectGoogleTranslateCombo();
    return;
  }
  if (mountingTarget?.isConnected) return;
  target.replaceChildren();
  mountingTarget = target;
  readinessObserver?.disconnect();
  readinessObserver = new MutationObserver(() => {
    googleTranslateGadget = target.querySelector(".goog-te-gadget");
    connectGoogleTranslateCombo();
  });
  readinessObserver.observe(target, { childList: true, subtree: true });
  loadTimer ||= setTimeout(showLoadFailure, 15000);
  try {
    new window.google.translate.TranslateElement({
      pageLanguage: "ja",
      includedLanguages: translationSettings.includedLanguages,
      autoDisplay: false,
    }, target.id);
    googleTranslateGadget = target.querySelector(".goog-te-gadget");
    connectGoogleTranslateCombo();
  } catch { showLoadFailure(); }
}

window.googleTranslateElementInit = mountGoogleTranslateWidgets;

function loadGoogleTranslateScript(useFallback = false) {
  clearTimeout(loadTimer);
  document.getElementById("google-translate-script")?.remove();
  const script = document.createElement("script");
  const fail = () => {
    script.remove();
    if (!useFallback && !window.google?.translate?.TranslateElement) loadGoogleTranslateScript(true);
    else showLoadFailure();
  };
  loadTimer = setTimeout(fail, 15000);
  script.id = "google-translate-script";
  script.src = useFallback ? translationSettings.fallbackScriptSrc : translationSettings.scriptSrc;
  script.async = true;
  script.onerror = fail;
  document.head.append(script);
}

export function ensureGoogleTranslate() {
  bindTranslationLayout();
  if (window.google?.translate?.TranslateElement) {
    mountGoogleTranslateWidgets();
    return;
  }
  if (loadTimer) return;
  const target = activeTarget();
  if (target) target.textContent = "翻訳を読み込んでいます…";
  loadGoogleTranslateScript();
}

export function selectTranslationTarget(id) { activeTranslateTargetId = id; }
