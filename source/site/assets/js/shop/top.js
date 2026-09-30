(() => {
  "use strict";

  new class {
    constructor() {
      this.keywordFieldElement = document.querySelector("#js-keyword-field");
      this.searchButtonElement = document.querySelector("#js-search-keyword");

      this.searchButtonElement?.addEventListener("click", this.searchKeyword.bind(this));

      this.keywordFieldElement?.addEventListener("keydown", (event) => {
        if (event.key !== "Enter") return;

        // 日本語入力の変換確定中は検索しない
        if (event.isComposing || event.keyCode === 229) return;

        event.preventDefault();
        this.searchKeyword();
      });
    }

    searchKeyword() {
      const keyword = this.keywordFieldElement?.value?.trim() || "";
      if (!keyword) return;

      const encodedKeyword = encodeURIComponent(keyword);
      const url = `/shop/search/?_filter=shop&_filter_value_name[]=${encodedKeyword}&_filter_cond_name[]=ct&_filter_value_activity_base[]=${encodedKeyword}&_filter_cond_activity_base[]=ct&_filter_and_or=OR`;

      window.location.href = url;
    }
  };
})();