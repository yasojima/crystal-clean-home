(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CCHCartCore = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';

  const MAX_QUANTITY = 9999;

  function quantity(value) {
    const number = typeof value === 'number' ? value : /^\d+$/.test(String(value)) ? Number(value) : NaN;
    if (!Number.isSafeInteger(number) || number < 0 || number > MAX_QUANTITY) {
      throw new Error('数量は0〜9,999の整数で入力してください。');
    }
    return number;
  }

  function normalize(lines, catalogue) {
    if (!Array.isArray(lines)) throw new Error('カートの形式を確認できません。');
    const totals = new Map();
    for (const line of lines) {
      if (!line || !Object.hasOwn(catalogue.items, line.key)) throw new Error('商品情報を確認できません。');
      const count = quantity(line.quantity);
      totals.set(line.key, quantity((totals.get(line.key) || 0) + count));
    }
    return [...totals].filter(([, count]) => count > 0).map(([key, count]) => ({key, quantity: count}));
  }

  function hasParent(lines, parentKey, catalogue) {
    return lines.some(line => line.quantity > 0 && (line.key === parentKey ||
      catalogue.items[line.key].includes?.includes(parentKey)));
  }

  function removeOrphans(lines, catalogue) {
    return lines.filter(line => {
      const parent = catalogue.items[line.key].parentKey;
      return !parent || hasParent(lines, parent, catalogue);
    });
  }

  function change(lines, key, value, catalogue, additive = false) {
    if (!Object.hasOwn(catalogue.items, key)) throw new Error('商品情報を確認できません。');
    const next = normalize(lines, catalogue);
    const current = next.find(line => line.key === key);
    const count = quantity(quantity(value) + (additive ? current?.quantity || 0 : 0));
    const parent = catalogue.items[key].parentKey;
    if (count > 0 && parent && !hasParent(next, parent, catalogue)) {
      throw new Error('このオプションの対象サービスを先にカートに追加してください。');
    }
    if (current) current.quantity = count;
    else if (count) next.push({key, quantity: count});
    return removeOrphans(next.filter(line => line.quantity > 0), catalogue);
  }

  function calculate(lines, catalogue) {
    const normalized = normalize(lines, catalogue);
    const groupCounts = new Map();
    for (const line of normalized) {
      const group = catalogue.items[line.key].quantityGroup;
      if (group) groupCounts.set(group, (groupCounts.get(group) || 0) + line.quantity);
    }
    let total = 0, count = 0, discount = 0, quoteCount = 0, approximate = false;
    const details = normalized.map(line => {
      const item = catalogue.items[line.key];
      if (item.parentKey && !hasParent(normalized, item.parentKey, catalogue)) {
        throw new Error('対象サービスのないオプションが含まれています。');
      }
      count += line.quantity;
      if (item.quote) {
        quoteCount += line.quantity;
        return {...line, item, unitPrice: null, amount: null, discount: 0};
      }
      const pricingQuantity = item.quantityGroup ? groupCounts.get(item.quantityGroup) : line.quantity;
      const tier = item.tiers.filter(t => t.min <= pricingQuantity).at(-1);
      if (!tier || !Number.isSafeInteger(tier.price) || tier.price < 0) throw new Error('価格を確認できません。');
      const amount = tier.price * line.quantity;
      const saved = (item.tiers[0].price - tier.price) * line.quantity;
      total += amount;
      discount += saved;
      approximate ||= item.approximate;
      if (!Number.isSafeInteger(total)) throw new Error('合計金額が計算可能な範囲を超えています。');
      return {...line, item, unitPrice: tier.price, amount, discount: saved};
    });
    // Published prices already include tax. Extract the tax once from the summed amount.
    const tax = Math.floor(total * catalogue.taxRate / (100 + catalogue.taxRate));
    return {details, total, count, discount, tax, subtotal: total - tax, quoteCount, approximate};
  }

  return {MAX_QUANTITY, quantity, normalize, hasParent, removeOrphans, change, calculate};
});
