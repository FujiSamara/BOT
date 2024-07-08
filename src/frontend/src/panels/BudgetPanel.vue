<template>
	<div class="budget-content">
		<div class="header"></div>
		<PanelTable
			v-model:tableBody="tableBody"
			:tableHead="tableHead"
			@click="onRowClicked"
			@checked="(val) => (rowsChecked = val)"
			@highlighted="(val) => (rowsHighlighted = val)"
		></PanelTable>
	</div>
</template>
<script setup lang="ts">
import PanelTable from "@/components/PanelTable.vue";
import { Ref, ref } from "vue";

const tableHead = [
	"ID",
	"Дата создания",
	"Дата закрытия",
	"Работник",
	"Сумма",
	"Тип оплаты",
	"Производство",
	"Цель платежа",
	"Статус",
	"Комментарий",
];

const tableBody: Ref<Array<{ id: number; columns: Array<String> }>> = ref([
	{
		columns: [
			"99",
			"2014.06.09",
			"2014.08.09",
			"9999",
			"Инфа на Сотку",
			"Безналичная",
			"Тольятти Автостроителей 56 Сайгина",
			"Оплата работ",
			"Согласовано КРУ",
			"Когда будет написано много текста, то он скорее всего будет просто пропадать и будут стоять точки, после 2-х строк",
		],
		id: 1,
	},
	{
		columns: [
			"99",
			"2014.06.09",
			"2014.08.09",
			"9999",
			"Инфа на Сотку",
			"Безналичная",
			"Тольятти Автостроителей 56 Сайгина",
			"Оплата работ",
			"Согласовано КРУ",
			"Когда будет написано много текста, то он скорее всего будет просто пропадать и будут стоять точки, после 2-х строк",
		],
		id: 2,
	},
	{
		columns: [
			"99",
			"2014.06.09",
			"2014.08.09",
			"9999",
			"Инфа на Сотку",
			"Безналичная",
			"Тольятти Автостроителей 56 Сайгина",
			"Оплата работ",
			"Согласовано КРУ",
			"Когда будет написано много текста, то он скорее всего будет просто пропадать и будут стоять точки, после 2-х строк",
		],
		id: 3,
	},
	{
		columns: [
			"99",
			"2014.06.09",
			"2014.08.09",
			"9999",
			"Инфа на Сотку",
			"Безналичная",
			"Тольятти Автостроителей 56 Сайгина",
			"Оплата работ",
			"Согласовано КРУ",
			"Когда будет написано много текста, то он скорее всего будет просто пропадать и будут стоять точки, после 2-х строк",
		],
		id: 4,
	},
]);

const rowsChecked: Ref<Array<{ checked: boolean; id: number }>> = ref([]);
const rowsHighlighted: Ref<Array<{ highlighted: boolean; id: number }>> = ref(
	[],
);

const onRowClicked = (rowIndex: number) => {
	console.log(rowIndex);
};
</script>
<style scoped>
.budget-content {
	width: 100%;
	height: 100%;
	display: flex;
	flex-direction: column;
	gap: 30px;
}
.header {
	width: 100%;
	height: 130px;
	border: 1px solid black;
}
</style>
