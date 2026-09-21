$(function(){
	function Mitsumori() {
		var self = this;

		var pageType = 1;

		var json = $('#formConfig').text();
		formConfig = $.parseJSON(json);

		var totalPriceElement = $('#totalPrice');
		var totalPrice = 0;
		var priceData = [];
		var totalDiscountPriceElement = $('#totalDiscount');
		var totalDiscountPriceContainerElement = $('.total-discount-container');
		var totalDiscountPrice = 0;

		var totalWorkHoursElement = $('.total-work-hours-value');
		var totalWorkHours = 0;

		var returnButtonElement = $('.return-button');
		var cartButtonElement = $('.cart-button');

		var enableOptionIds = [];

		var formErrors = [];

		// URLでセクションが指定されている場合は該当箇所までスクロール
		initialScroll();
		// inputフィールドにイベントをセット
		setInputEvent();
		// セクション見出しバー開閉
		setTitleBarEvent();
		// 画面右下のアイコンクリック時のイベント設定
		setFormLinkEvent();
		// フッターのリンクアイコン設定
		setFooterLinkIcon();
		// スクロール時にページNoを固定表示
		setScrollFixPageNoList();
		// 戻るボタンのイベントをセット
		setReturnButton();
		// カートボタンのイベントをセット
		setCartButton();
		// セクションの説明ボタンのイベントをセット
		setSectionButton();
		// SP用数値入力モーダルのイベントをセット
		setCalculator();

		// フォームからブラウザの戻るボタンで戻った際の表示対応
		setTimeout(function() {
			// 入力済みの項目が存在するセクションは表示
			openSection();
			updateScreen();
		}, 10);

		// URLでセクションが指定されている場合は該当箇所までスクロール
		function initialScroll() {
			var section = getParam('section');
			var noscroll = getParam('noscroll');
			if (!noscroll && section && $('#section-' + section).length) {
				$('html,body').animate({scrollTop:$('#section-' + section).offset().top});
			}
		}

		// inputフィールドにイベントをセット
		function setInputEvent() {
			$('input').blur(function() {
				var inputType = $(this).attr('data-type');
				var inputMax = $(this).attr('data-max');
				if (!inputMax) {
					inputMax = 99;
				}
				var target = $(this);
				var targetValue = target.val();

				if (inputType === 'numberButton' || inputType === 'numberInput') {
					if (isIntText(targetValue)) {
						if (Number(targetValue) > Number(inputMax)) {
							target.val(inputMax);
						}
					} else {
						target.val(0);
					}
					updateScreen();
				}

				// リアルタイムバリデーション
				realtimeValidateForm($(this));
			});

			$('input').focus(function() {
				var inputType = $(this).attr('data-type');
				var target = $(this);
				var targetValue = target.val();

				// 入力しやすいよう、フォーカス時に0を消す
				if (inputType === 'numberButton' || inputType === 'numberInput') {
					if (targetValue == 0) {
						target.val('');
					}
				}

				// 面積用のinputは、専用の数値入力用モーダルを開く
				if (inputType === 'numberInput') {
					openCalculator($(this));
				}
			});

			$('input').click(function() {
				var inputType = $(this).attr('data-type');
				var targetId = $(this).attr('data-target');
				var target = $('#' + targetId);
				var targetValue = target.val();

				// セクションの中で、一要素のみ入力できるようにする (radioの他属性対応版)
				sectionSingleFilter($(this));

				switch (inputType) {
					// 数値増加ボタン
					case 'numberButtonPlus':
						if (isIntText(targetValue)) {
							if (targetValue < 99) {
								target.val(++targetValue);
							}
						} else {
							// 数値以外が入力されている場合は0をセット
							target.val(0);
						}
						updateScreen();
						break;
					// 数値減少ボタン
					case 'numberButtonMinus':
						if (isIntText(targetValue)) {
							if (targetValue > 0) {
								target.val(--targetValue);
							}
						} else {
							target.val(0);
						}
						updateScreen();
						break;
					case 'checkbox':
						updateScreen();
						break;
					case 'radio':
						var inputElements = $(this).parents('.row').find('input');
						var clickedId = $(this).attr('id');
						inputElements.each(function(index, element) {
							if (clickedId == $(element).attr('id')) {
								$(element).prop('checked', true);
							} else {
								$(element).prop('checked', false);
							}
						});
						updateScreen();
						break;
				}

				// リアルタイムバリデーション
				realtimeValidateForm($(this));
			});
		}

		// セクションの中で、一要素のみ入力できるようにする (radioの他属性対応版)
		function sectionSingleFilter(element) {
			var targetId = element.attr('id');
			if (!targetId) targetId = element.attr('data-target');
			var fieldConfig = getFieldConfig(targetId);
			if (!fieldConfig || fieldConfig.type !== 'menu' || !fieldConfig.section || !fieldConfig.section.single) {
				return
			}

			$.each(fieldConfig.section.fields, function(fieldIndex, field) {
				if (targetId !== field.id) {
					var fieldElement = $('#' + field.id);
					if (field.type == 'radio' || field.type == 'checkbox') {
						fieldElement.prop('checked', false);
					} else {
						fieldElement.val(0);
					}
				}
			});

			updateScreen();
		}

		// 画面更新
		function updateScreen() {
			// 料金計算
			calcAllField();
			// 子要素の表示変更
			changeChildFields();
			// カートボタン表示切り替え
			// if (totalPrice > 0) {
			// 	cartButtonElement.css('display', 'inline-block');
			// } else {
			// 	cartButtonElement.css('display', 'none');
			// }
		}

		// 全フィールド 見積もり金額計算
		function calcAllField() {
			totalPrice = 0;
			totalDiscountPrice = 0;
			totalWorkHours = 0;
			priceData = [];

			// 無効な項目に値が入力されている場合はクリア (戻るボタン対応のため)
			enableOptionIds = getEnableOptionIds();
			if (formConfig.option && formConfig.option.fields) {
				$.each(formConfig.option.fields, function(fieldIndex, field) {
					var fieldElement = $('#' + field.id)
					if ($.inArray(field.id, enableOptionIds) === -1) {
						if (field.type == 'radio' || field.type == 'checkbox') {
							fieldElement.prop('checked', false);
						} else {
							fieldElement.val(0);
						}
					}
				});
			}

			// 水回りセット
			if (formConfig.set && formConfig.set.mizumawariSet) {
				var mizumawariSetData = getMizumawariSetData();
				if (mizumawariSetData.count) {
					var totalPriceBeforeMizumawariSet = totalPrice;
					// チェックした項目の数をカウント
					setCount = mizumawariSetData.count;
					// 一定数以上の場合
					var setConfig = formConfig.set.mizumawariSet;

					var mizumawariSetItems = [];
					$.each(mizumawariSetData.setMenus, function(k, v) {
						mizumawariSetItems.push({
							'name': 'menu-' + k,
							'value': v,
						});
					});

					if (setConfig.setPriceMore && setCount >= setConfig.setPriceMore.min) {
						var moreCount = setCount - setConfig.setPriceMore.min;
						var price = setConfig.setPriceMore.price + (setConfig.setPriceMore.unitPrice * moreCount);
						totalPrice = price;
						totalWorkHours = setConfig.setPriceMore.workHours;

						if (setCount) {
							priceData.push({
								'name': 'set-mizumawariSet',
								'value': setCount,
								'price': price,
								'items': mizumawariSetItems,
							});
						}
					} else {
						// 一致する数のセットの金額と作業時間を適用
						$.each(setConfig.setPrice, function(fieldIndex, setPriceData) {
							if (setPriceData.count == setCount) {
								totalPrice = setPriceData.price;
								totalWorkHours = setPriceData.workHours;

								if (setCount) {
									priceData.push({
										'name': 'set-mizumawariSet',
										'value': setCount,
										'price': setPriceData.price,
										'items': mizumawariSetItems,
									});
								}

								return false;
							}
						});
					}
					// 水回りセット適用時の割引金額を計算
					var mizumawariSetTotalPrice = totalPrice - totalPriceBeforeMizumawariSet;
					totalDiscountPrice += calcMizumawariSetDiscountPrice(mizumawariSetTotalPrice, mizumawariSetData);
				}
			}

			// 通常メニュー
			$.each(formConfig.pages, function(pageIndex, page) {
				$.each(page.sections, function(sectionIndex, section) {
					$.each(section.fields, function(fieldIndex, field) {
						var fieldElement = $('#' + field.id)
						var fieldValue = getFieldValue(fieldElement, field);
						if (mizumawariSetData && mizumawariSetData.count && field.id in mizumawariSetData.remainingMenus) {
							fieldValue = mizumawariSetData.remainingMenus[field.id];
						}
						// 見積もり金額計算
						var price = calcPrice(fieldValue, field)
						totalPrice += price;
						// 作業目安時間計算
						totalWorkHours += calcWorkHours(fieldValue, field);
						// 背景色設定
						setBgColor(fieldElement, field);

						if (fieldValue) {
							priceData.push({
								'name': 'menu-' + field.id,
								'serviceName': section.name + field.name,
								'value': fieldValue,
								'price': price,
							});
						}
					});
					// セクション見出しバー色付け
					setSectionBarColor(section);
				});
			});

			// オプション
			if (formConfig.option && formConfig.option.fields) {
				$.each(formConfig.option.fields, function(fieldIndex, field) {
					var fieldElement = $('#' + field.id)
					var fieldValue = getFieldValue(fieldElement, field);
					// 見積もり金額計算
					var price = calcPrice(fieldValue, field);
					totalPrice += price;
					// 作業目安時間計算
					totalWorkHours += calcWorkHours(fieldValue, field);
					// 背景色設定
					setBgColor(fieldElement, field);

					if (fieldValue) {
						priceData.push({
							'name': 'option-' + field.id,
							'value': fieldValue,
							'price': price,
						});
					}
				});
			}

			// グループ割引 同じグループのメニューを一定個数以上選択で割引
			groupDiscount();

			if (totalWorkHours >= 7.5) {
				totalWorkHoursElement.text('要問合');
			} else {
				totalWorkHoursElement.text(numberFormat(totalWorkHours) + '時間');
			}
			totalPriceElement.text(numberFormat(totalPrice));

			totalDiscountPriceElement.text(totalDiscountPrice);
			if (totalDiscountPrice > 0) {
				totalDiscountPriceContainerElement.css('display', 'inline-block');
			} else {
				totalDiscountPriceContainerElement.css('display', 'none');
			}
		}

		// 水回りセット計算用のデータを準備
		// - セット対象の点数と、セット対象メニューでセットとしてカウントされない数を返却
		function getMizumawariSetData() {
			var setMenuTargetMenus = {};
			var setMenus = {};
			// セット料金対象メニューの入力個数をカウント
			$.each(formConfig.pages, function(pageIndex, page) {
				$.each(page.sections, function(sectionIndex, section) {
					$.each(section.fields, function(fieldIndex, field) {
						var fieldElement = $('#' + field.id);
						if (field.set === 'mizumawariSet') {
							if (field.type == 'radio' || field.type == 'checkbox') {
								if (fieldElement.prop('checked')) {
									setMenuTargetMenus[field.id] = 1;
								}
							} else {
								setMenuTargetMenus[field.id] = Number(fieldElement.val());
							}
						}
					});
				});
			});

			var setMenuCount = 0;

			// 洗面所とトイレはセットで1点としてカウント
			if (setMenuTargetMenus.washroom && setMenuTargetMenus.toilet) {
				if (setMenuTargetMenus.washroom > setMenuTargetMenus.toilet) {
					pointCount = setMenuTargetMenus.toilet;
				} else {
					pointCount = setMenuTargetMenus.washroom;
				}
				setMenuCount += pointCount;
				setMenuTargetMenus.toilet -= pointCount;
				setMenuTargetMenus.washroom -= pointCount;
				setMenus['mizumawariSetWashroomPlusToilet'] = pointCount;
			}

			// トイレは2個で1点としてカウント
			var toilePointCount = 2;
			if (setMenuTargetMenus.toilet >= toilePointCount) {
				var pointCount = Math.floor(setMenuTargetMenus.toilet / toilePointCount);
				setMenuTargetMenus.toilet -= pointCount * toilePointCount;
				setMenuCount += pointCount;
				setMenus['mizumawariSetToilet2'] = pointCount;
			}

			// それ以外は1個で1点
			var menuIdConvertList = {
				'kitchen': 'mizumawariSetKitchen',
				'rangeHood': 'mizumawariSetRangeHood',
				'bathroom': 'mizumawariSetBathroom',
			}
			$.each(setMenuTargetMenus, function(setMenuId, setMenuValue) {
				if (!setMenuValue) {
					return true;
				}
				if (setMenuId === 'washroom' || setMenuId === 'toilet') {
					return true;
				}
				setMenuTargetMenus[setMenuId] -= setMenuValue;
				setMenuCount += setMenuValue;

				// 単品メニューをセットメニューのメニューとしてカウント
				if (menuIdConvertList[setMenuId]) {
					if (!setMenus[menuIdConvertList[setMenuId]]) {
						setMenus[menuIdConvertList[setMenuId]] = 0;
					}
					setMenus[menuIdConvertList[setMenuId]] += setMenuValue;
				} else {
					if (!setMenus[setMenuId]) {
						setMenus[setMenuId] = 0;
					}
					setMenus[setMenuId] += setMenuValue;
				}
			});

			if (setMenuCount < 2) {
				setMenuCount = 0;
				setMenuTargetMenus = {};
				setMenus = {};
			}

			return {'remainingMenus': setMenuTargetMenus, 'setMenus': setMenus, 'count': setMenuCount};
		}

		// フィールド 見積もり金額計算
		function calcPrice(value, fieldConfig) {
			if (!isIntText(value) || value == 0 || !fieldConfig.price) {
				return 0;
			}

			// 特定のメニューが選択されているかどうかで料金が変わるメニュー
			if ($.isArray(fieldConfig.price)) {
				var enablePrice = false;
				$.each(fieldConfig.price, function(key, priceConfig) {
					var belongsElement = $('#' + priceConfig.belongsTo);
					var belongsValue = belongsElement.val();
					var belongsElementType = belongsElement.attr('data-type');

					if (belongsElementType == 'radio' || belongsElementType == 'checkbox') {
						if (belongsElement.prop('checked')) {
							fieldConfig = priceConfig;
							enablePrice = true;
							return false;
						}
					} else if (isIntText(belongsValue) && belongsValue != 0) {
						fieldConfig = priceConfig;
						enablePrice = true;
						return false;
					}
				});
				if (!enablePrice) {
					return 0;
				}
			}

			// 最低請負価格設定時
			if (fieldConfig.minimumContractPrice && fieldConfig.minimumContractCount) {
				if (value < fieldConfig.minimumContractCount) {
					return fieldConfig.minimumContractPrice;
				} else {
					return ((value - 24) * fieldConfig.price) + 24200;
				}
			// 2台目値段設定時
			} else if (fieldConfig.secondPrice && value > 1) {
				return fieldConfig.price + ((value - 1) * fieldConfig.secondPrice);
			} else {
				return value * fieldConfig.price;
			}

			return 0;
		}

		// 水回りセット適用時の割引金額を計算
		function calcMizumawariSetDiscountPrice(mizumawariSetTotalPrice, mizumawariSetData) {
			// セットを単体メニューに変換
			var singleMenus = {};
			$.each(mizumawariSetData.setMenus, function(setId, setCount) {
				var setConfig = getFieldConfig(setId);
				if (!setConfig || !setConfig.field.setItems) {
					return true;
				}
				$.each(setConfig.field.setItems, function(setItemKey, setItem) {
					if (!singleMenus[setItem.id]) {
						singleMenus[setItem.id] = 0;
					}
					singleMenus[setItem.id] += setItem.count * setCount;
				});
			});

			// 単体メニューとして金額を計算
			var mizumawariSetSingleMenuTotalPrice = 0;
			$.each(singleMenus, function(menuId, menuCount) {
				var fieldConfig = getFieldConfig(menuId);
				var menuPrice = calcPrice(menuCount, fieldConfig.field);
				mizumawariSetSingleMenuTotalPrice += menuPrice;
			});

			return mizumawariSetSingleMenuTotalPrice - mizumawariSetTotalPrice;
		}

		// グループ割引 同じグループのメニューを一定個数以上選択で割引
		function groupDiscount() {
			if (!formConfig.groupDiscount) return;
			$.each(formConfig.groupDiscount, function(groupId, group) {
				var groupCount = 0;
				$.each(formConfig.pages, function(pageIndex, page) {
					$.each(page.sections, function(sectionIndex, section) {
						$.each(section.fields, function(fieldIndex, field) {
							if (field.groupDiscount && $.inArray(groupId, field.groupDiscount) !== -1) {
								var fieldElement = $('#' + field.id)
								groupCount += Number(getFieldValue(fieldElement, field));
							}
						});
					});
				});
				if (groupCount >= group.minimumCount) {
					var discountPrice = group.discountPrice * (groupCount - 1);
					priceData.push({
						'name': 'groupDiscount-' + groupId,
						'value': groupCount - 1,
						'price': discountPrice,
					});
					totalPrice -= discountPrice;
					totalDiscountPrice += discountPrice;
				}
			});
		}

		// フィールド 作業目安時間計算
		function calcWorkHours(value, fieldConfig) {
			if (!isIntText(value) || value == 0 || !fieldConfig.workHours) {
				return 0;
			}

			return value * fieldConfig.workHours;
		}

		// フィールドの値を取得
		function getFieldValue(fieldElement, fieldConfig) {
			value = fieldElement.val();

			if (!isIntText(value) || value == 0) {
				return 0;
			}

			if (fieldConfig.type == 'radio' || fieldConfig.type == 'checkbox') {
				if (fieldElement.prop('checked')) {
					// referenceが設定されている場合は他の項目の値を参照
					if (fieldConfig.reference) {
						value = 0;
						$.each(fieldConfig.reference, function(key, referenceId) {
							if ($('#' + referenceId).val()) {
								value += Number($('#' + referenceId).val());
							}
						});
					}
					return value;
				} else {
					return 0;
				}
			} else {
				return value;
			}

			return 0;
		}

		// 入力項目の背景色を設定
		function setBgColor(fieldElement, fieldConfig) {
			var value = fieldElement.val();
			var card = fieldElement.parents('.card');

			card.removeClass('selected-card')
			if (fieldConfig.type == 'radio' || fieldConfig.type == 'checkbox') {
				if (fieldElement.prop('checked')) {
					card.addClass('selected-card')
				}
			} else if (isIntText(value) && value != 0) {
				card.addClass('selected-card')
			}
		}

		// セクション見出しバー色付け
		function setSectionBarColor(section) {
			var isSelectedSection = false
			$.each(section.fields, function(fieldIndex, field) {
				var fieldElement = $('#' + field.id)
				var fieldValue = fieldElement.val();
				if (field.checked) {
					return true;
				}
				if (field.type == 'radio' || field.type == 'checkbox') {
					if (fieldElement.prop('checked')) {
						isSelectedSection = true;
						return false;
					}
				} else if (isIntText(fieldValue) && fieldValue != 0) {
					isSelectedSection = true;
					return false;
				}
			});

			var sectionBarElement = $('#section-' + section.id);
			if (isSelectedSection) {
				sectionBarElement.addClass('selected-type-bar');
			} else {
				sectionBarElement.removeClass('selected-type-bar');
			}
		}

		// 数値を3桁カンマ区切りに変換
		function numberFormat(value) {
			return String(value).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
		}

		// 子要素の表示変更
		function changeChildFields() {
			$.each(formConfig.pages, function(pageIndex, page) {
				$.each(page.sections, function(sectionIndex, section) {
					$.each(section.fields, function(fieldIndex, field) {
						// 子要素の表示切り替え
						toggleChildField(field);
						// 子要素の金額表示切り替え
						changeChildPrice(field);
					});
				});
			});
		}

		// 子要素の表示切り替え
		function toggleChildField(field) {
			if (!field.belongsTo) return;

			var belongsElement = $('#' + field.belongsTo);
			var belongsValue = belongsElement.val();
			var belongsElementType = belongsElement.attr('data-type');
			var childElementBlock = $('#menu-' + field.id);
			var childElement = $('#' + field.id);
			var childValue = childElement.val();

			var show = false;

			if (belongsElementType == 'radio' || belongsElementType == 'checkbox') {
				if (belongsElement.prop('checked')) {
					show = true;
				}
			} else if (isIntText(belongsValue) && belongsValue != 0) {
				show = true;
			}
			if (show) {
				childElementBlock.removeClass('hide');
			} else {
				childElementBlock.addClass('hide');
				if (field.type == 'radio' || field.type == 'checkbox') {
					childElement.prop('checked', false);
				} else {
					childElement.val('');
				}
			}
		}

		// 子要素の金額表示切り替え
		function changeChildPrice(field) {
			if (!$.isArray(field.price)) return;

			var fieldPriceConfig = null;
			$.each(field.price, function(key, priceConfig) {
				var belongsElement = $('#' + priceConfig.belongsTo);
				var belongsValue = belongsElement.val();
				var belongsElementType = belongsElement.attr('data-type');

				if (belongsElementType == 'radio' || belongsElementType == 'checkbox') {
					if (belongsElement.prop('checked')) {
						fieldPriceConfig = priceConfig;
						return false;
					}
				} else if (isIntText(belongsValue) && belongsValue != 0) {
					fieldPriceConfig = priceConfig;
					return false;
				}
			});

			var priceElement = $('#menu-' + field.id + ' .price');
			if (priceElement.length) {
				if (fieldPriceConfig) {
					var priceHtml = '';
					if (fieldPriceConfig.priceDisplayPrefix) {
						priceHtml = fieldPriceConfig.priceDisplayPrefix + ' ';
					}
					priceHtml += numberFormat(fieldPriceConfig.price) + '円';
					priceElement.html(priceHtml);
				} else {
					priceElement.html('');
				}
			}
		}

		// セクション見出しバー開閉
		function setTitleBarEvent() {
			$('.type-bar').click(function() {
				var sectionBody = $(this).next();
				var arrow = $(this).find('.type-bar-arrow');
				if (sectionBody.is(':visible')) {
					sectionBody.addClass('hide');
          arrow.addClass('plus');
          arrow.removeClass('minus');
				} else {
					sectionBody.removeClass('hide');
          arrow.removeClass('plus');
          arrow.addClass('minus');
					$('html,body').animate({scrollTop:$(this).offset().top});
				}
			});
		}

		// 画面右下のアイコンクリック時のイベント設定
		function setFormLinkEvent() {
			$('.footer-link').click(function() {
				if (!validateForm()) {
					var alertMessage = '＊入力内容をご確認ください';
					$.each(formErrors, function(errorIndex, errorMessage) {
						alertMessage += "<br>・" + errorMessage
					});
					alertModal(alertMessage);
					return false;
				}

				if (pageType == 'option') {
					// フォームに遷移
					jumpToForm();
				} else {
					// 最終ページ
					if (formConfig.pages.length == pageType) {
						// 入力した商品に紐づくオプションのIDを取得
						enableOptionIds = getEnableOptionIds();
						if (enableOptionIds.length) {
							var optionText = getOptions(enableOptionIds, true);
							confirmModal('有料オプションサービスを確認しますか？<div class="modal-option-text">' + optionText + '</div>').then(
								function(type) {
									if (type === 'primary') {
										// オプションを表示
										showOptions();
										$('html,body').animate({ scrollTop:0 }, 0);
									} else if(type === 'secondary') {
										// フォームに遷移
										jumpToForm();
									}
								}
							);
						} else {
							// フォームに遷移
							jumpToForm();
						}
					} else {
						pageType++;
						$('.main-page').addClass('hide');
						$('.main-page-' + pageType).removeClass('hide');
						$('html,body').animate({ scrollTop:0 }, 0);
					}
				}
				setFooterLinkIcon();
			});
		}

		// フッターのリンクアイコン設定
		function setFooterLinkIcon() {
			// 最終ページの場合はメールアイコン
			if (pageType == 'option' || formConfig.pages.length == pageType) {
				$('.footer-link .fa-envelope').removeClass('hide');
				$('.footer-link .icon_hikouki').removeClass('hide');
				$('.footer-link .fa-arrow-right').addClass('hide');
				$('.footer-link-text').text('問い合わせ');
			// それ以外は矢印アイコン
			} else {
				$('.footer-link .fa-arrow-right').removeClass('hide');
				$('.footer-link .fa-envelope').addClass('hide');
				$('.footer-link .icon_hikouki').addClass('hide');
				$('.footer-link-text').text('次へ');
			}
		}

		// バリデーション実行
		function validateForm() {
			formErrors = [];

			$.each(formConfig.pages, function(pageIndex, page) {
				if (pageIndex + 1 != pageType) return true;

				$.each(page.sections, function(sectionIndex, section) {
					if (section.id === 'mizumawariSet') {
						var sectionFieldCount = 0;
						var setCountMatch = false;
						$.each(section.fields, function(fieldIndex, field) {
							var fieldElement = $('#' + field.id);
							var value = getFieldValue(fieldElement, field);
							sectionFieldCount += Number(value);
						});
						if (sectionFieldCount == 1) {
							var enableSet = false;
							$.each(priceData, function(priceValueIndex, priceValue) {
								if (priceValue.name == 'set-mizumawariSet') {
									enableSet = true;
									return false;
								}
							});
							if (!enableSet) {
								formErrors.push('お得な水回りセットをご利用の際は、2点以上ご選択ください');
							}
						}
					}
					if (section.validations) {
						$.each(section.validations, function(validationIndex, validation) {
							var sectionFieldCount = 0;
							// 入力必須確認
							if (validation.rule[0] === 'require') {
								$.each(section.fields, function(fieldIndex, field) {
									var fieldElement = $('#' + field.id);
									var value = fieldElement.val();
									if (field.type == 'radio' || field.type == 'checkbox') {
										if (fieldElement.prop('checked')) {
											sectionFieldCount++;
										}
									} else if (!isIntText(value) || value > 0) {
										sectionFieldCount++;
									}
								});
								if (!sectionFieldCount) {
									formErrors.push(validation.message);
								}
							}
						});
					}
				});
			});

			if (formErrors.length) return false;

			return true;
		}

		// リアルタイムバリデーション
		function realtimeValidateForm(eventElement) {
			// ゴミ回収 最大選択数3つまで
			var gomiKaishu = $('#gomiKaishu')
			if (Number(gomiKaishu.val()) > 3) {
				alertModal('ゴミ回収の最大選択数は3つまでです')
				gomiKaishu.val(3);
				updateScreen();
			}
		}

		// 入力した商品に紐づくオプションのIDを取得
		function getEnableOptionIds() {
			var optionIds = [];
			$.each(formConfig.pages, function(pageIndex, page) {
				$.each(page.sections, function(sectionIndex, section) {
					$.each(section.fields, function(fieldIndex, field) {
						var fieldElement = $('#' + field.id)
						var value = fieldElement.val();

						if (field.type == 'radio' || field.type == 'checkbox') {
							if (fieldElement.prop('checked') && field.options) {
								$.merge(optionIds, field.options)
							}
						} else if (isIntText(value) && value != 0 && field.options) {
							$.merge(optionIds, field.options)
						}
					});
				});
			});
			// 重複した値を取り除く
			optionIds =  optionIds.filter(function(el, index, arr) {
				return index === arr.indexOf(el);
			});
			return optionIds;
		}

		// オプションIDからオプションを取得
		function getOptions(optionIds, toText) {
			var options = [];
			$.each(formConfig.option.fields, function(optionIndex, option) {
				if ($.inArray(option.id, optionIds) !== -1) {
					options.push(option);
				}
			});

			if (toText) {
				var optionNameText = '';
				$.each(options, function(optionIndex, option) {
					var optionName = option.name.replace(/<.*?>/, '');
					optionNameText += '・' + optionName + '<br>';
				});
				return optionNameText;
			}

			return options;
		}

		// オプションを表示
		function showOptions() {
			pageType = 'option';
			$('.main-page').addClass('hide');
			$('.main-options').removeClass('hide');

			// 選択した商品と紐付いている、有効なオプションのみ表示
			if (formConfig.option && formConfig.option.fields) {
				$.each(formConfig.option.fields, function(fieldIndex, field) {
					var divElement = $('#option-' + field.id)
					if ($.inArray(field.id, enableOptionIds) !== -1) {
						divElement.removeClass('hide');
					} else {
						divElement.addClass('hide');
					}
				});
			}
		}

		// フォームに遷移
		function jumpToForm() {
			// 見積もり項目を選択していない場合はフォームに遷移しない
			if (!totalPrice) {
				alertModal('お見積り項目を選択してください<br>※お見積金額が0円の場合はフォームに進めません');
				return;
			}

			var formLink = formConfig.form;

			var mitsumoriSendForm = $('#mitsumoriSendForm');
			mitsumoriSendForm.find('[name="mitsumori_price"]').val(totalPrice);
			mitsumoriSendForm.find('[name="mitsumori_work_hours"]').val(totalWorkHours);

			// フォームの入力値をjsonに変換
			var formData = [];
			formData.push({'name': 'formId', 'value': formConfig.id});
			formData = $.merge(formData, priceData);

			var json = JSON.stringify(formData);

			mitsumoriSendForm.find('[name="mitsumori_json"]').val(json);

			mitsumoriSendForm.attr('action', formLink);
			mitsumoriSendForm.submit();
		}

		// 整数判定 型は問わない
		function isIntText(num) {
			num = String(num);
			return (num.match(/^\d+$/));
		}

		// 確認用モーダル
		function confirmModal(message) {
			var defer = $.Deferred();
			var modalElement = $('#confirmModal');

			modalElement.find('.btn-primary').off('click');
			modalElement.off('hide.bs.modal');

			modalElement.find('.modal-body').html(message);
			modalElement.modal('show');

			modalElement.find('.btn-primary').click(function() {
				defer.resolve('primary');
				modalElement.modal('hide');
				return true;
			});
			modalElement.find('.btn-secondary').click(function() {
				defer.resolve('secondary');
				modalElement.modal('hide');
				return true;
			});
			return defer.promise();
		}

		// アラートモーダル
		function alertModal(message) {
			var modalElement = $('#alertModal');
			modalElement.modal({
				backdrop: 'static',
			});
			modalElement.find('.modal-body').html(message);
		}

		// 説明モーダル
		function descriptionModal(text, youtubeUrl) {
			var modalElement = $('#descriptionModal');
			modalElement.modal({
				backdrop: 'static',
			});
			modalElement.find('.modal-text').html(text);

			modalElement.find('.modal-video').hide();
			if (youtubeUrl) {
				var match = youtubeUrl.match(/\?v=(\w+)/);
				if (match) {
					var youtubeEmbedUrl = 'https://www.youtube.com/embed/' + match[1];
					modalElement.find('iframe').attr('src', youtubeEmbedUrl);
					modalElement.find('.modal-video').show();
				}
			}
		}

		// 説明モーダル更新
		function updateDescriptionModal(text) {
			var modalElement = $('#descriptionModal');
			modalElement.find('.modal-text').html(text);
		}

		// URLパラメータ取得
		function getParam(name, url) {
			if (!url) url = window.location.href;
			name = name.replace(/[\[\]]/g, "\\$&");
			var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
				results = regex.exec(url);
			if (!results) return null;
			if (!results[2]) return '';
			return decodeURIComponent(results[2].replace(/\+/g, " "));
		}

		// スクロール時にページNoを固定表示
		function setScrollFixPageNoList() {
			var pageNoListElement = $('.page-no-list');
			if (pageNoListElement.length) {
				$(window).on('scroll',function(){
					if ($(window).scrollTop() > $('.header').height()){
						pageNoListElement.addClass('fixed');
					} else {
						pageNoListElement.removeClass('fixed');
					}
				});
				$(window).trigger('scroll');
			}
		}

		// 戻るボタン
		function setReturnButton() {
			returnButtonElement.click(function() {
				if (pageType === 1) {
					if (document.referrer) {
						history.back();
					} else {
						location.href = '../../';
					}
				} else if (pageType === 'option') {
					pageType = formConfig.pages.length;
				} else {
					pageType--;
				}

				$('.main-options').addClass('hide');
				$('.main-page').addClass('hide');
				$('.main-page-' + pageType).removeClass('hide');
				$('html,body').animate({ scrollTop:0 }, 0);
				setFooterLinkIcon();
			});
		}

		// カートボタン
		function setCartButton() {
			cartButtonElement.click(function() {
				var formData = [];
				formData.push({'name': 'formId', 'value': formConfig.id});
				formData = $.merge(formData, priceData);
				descriptionModal('<div class="text-center"><div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div></div>');
				var json = JSON.stringify(formData);
				$.post('/mitsumori/cart', {formData: json}).done(function(data) {
					updateDescriptionModal(data.replace(/\r\n|\r|\n/g, '<br>'));
				});
			});
		}

		// セクションの説明ボタンのイベントをセット
		function setSectionButton() {
			$('.section-button').click(function() {
				if ($(this).attr('data-url')) {
					window.open($(this).attr('data-url'));
				} else if ($(this).attr('data-text')) {
					descriptionModal($(this).attr('data-text'), $(this).attr('data-youtubeUrl'));
				}
			});
			// モーダルを閉じたら動画を消す
			$('#descriptionModal').on('hidden.bs.modal', function() {
				$('#descriptionModal iframe').attr('src', '');
			});
		}

		// 入力済みの項目が存在するセクションは表示
		function openSection() {
			$.each(formConfig.pages, function(pageIndex, page) {
				$.each(page.sections, function(sectionIndex, section) {
					var sectionElement = $('#section-' + section.id);
					var sectionBody = sectionElement.next();
					var arrow = sectionElement.find('.type-bar-arrow');

					$.each(section.fields, function(fieldIndex, field) {
						var fieldElement = $('#' + field.id)
						var fieldValue = getFieldValue(fieldElement, field);
						if (fieldValue) {
							sectionBody.removeClass('hide');
              arrow.removeClass('plus');
							arrow.addClass('minus');
						}
					});
				});
			});
		}

		// 指定したIDの設定情報を取得
		function getFieldConfig(targetId) {
			var result = false;

			$.each(formConfig.pages, function(pageIndex, page) {
				$.each(page.sections, function(sectionIndex, section) {
					$.each(section.fields, function(fieldIndex, field) {
						if (field.id === targetId) {
							result = {
								'type': 'menu',
								'field': field,
								'section': section,
							};
							return false;
						}
					});
					if (result) return false;
				});
				if (result) return false;
			});

			if (formConfig.option && formConfig.option.fields) {
				$.each(formConfig.option.fields, function(fieldIndex, field) {
					if (field.id === targetId) {
						result = {
							'type': 'option',
							'field': field,
						};
						return false;
					}
				});
			}

			return result;
		}

		var calculatorNumber = '';
		var calculatorMax = 0;
		var calculatorTarget;

		// SP用数値入力モーダルのイベントをセット
		function setCalculator() {
			// 数字ボタン
			$('#calculator .number').click(function() {
				// 入力値が0で、さらに0を入力しようとした場合はreturn
				if (! calculatorNumber && $(this).text() == 0) return;

				calculatorNumber += $(this).text();

				// 数値制限
				if (Number(calculatorNumber) > Number(calculatorMax)) {
					calculatorNumber = calculatorMax;
				}

				$('#calculator .display-number').text(calculatorNumber);
			});
			// クリアボタン
			$('#calculator .clear').click(function() {
				calculatorNumber = '';
				$('#calculator .display-number').text('0');
			})
			// OKボタン
			$('#calculator .ok').click(function() {
				if (calculatorNumber) {
					calculatorTarget.val(calculatorNumber);
				} else {
					calculatorTarget.val(0);
				}
				$('#calculator').modal('hide');
				updateScreen();
			})
			// モーダルを閉じたら数値をクリア
			$('#calculator').on('hidden.bs.modal', function() {
				calculatorNumber = '';
				$('#calculator .display-number').text('0');
			});
		}

		// SP用数値入力モーダルを開く
		function openCalculator(inputElement) {
			// SP以外はreturn
			if (!navigator.userAgent.match(/Android|iPhone/i)) {
				return;
			}

			calculatorTarget = inputElement;
			// 初期値
			if (isIntText(inputElement.val())) {
				calculatorNumber = inputElement.val();
				$('#calculator .display-number').text(calculatorNumber);
			}
			// 数値制限
			calculatorMax = 99;
			if (inputElement.attr('data-max')) {
				calculatorMax = inputElement.attr('data-max');
			}

			$('#calculator').modal('show');
		}
	}

	var Mitsumori = new Mitsumori();
});
