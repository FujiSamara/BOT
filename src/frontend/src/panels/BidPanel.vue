<template>
	<div class="bid-content">
		<div class="header-content">
			<h1>Заявки</h1>
			<PanelTools class="top-tools">
				<PeriodTool
					v-if="!elementViewing"
					v-model:from-date="fromDateString"
					v-model:to-date="toDateString"
				></PeriodTool>
				<ToolSeparator v-if="!elementViewing"></ToolSeparator>
				<SeacrhTool
					v-if="!elementViewing"
					id="topSearch"
					v-model:value="searchString"
				></SeacrhTool>
				<ToolSeparator v-if="!elementViewing"></ToolSeparator>
				<ExportTool></ExportTool>
			</PanelTools>
		</div>
		<PanelTable
			v-if="!elementViewing"
			:table="table"
			@click="onRowClicked"
			:can-delete="true"
			:can-approve="true"
			:can-reject="true"
		></PanelTable>
		<ViewPanelRow
			v-if="elementViewing"
			:viewer="viewer!"
			class="view-page"
		></ViewPanelRow>
	</div>
</template>
<script setup lang="ts">
import PanelTable from "@/components/PanelTable.vue";
import ViewPanelRow from "@/components/ViewPanelRow.vue";
import PanelTools from "@/components/PanelTools.vue";
import SeacrhTool from "@/components/PanelTools/SearchTool.vue";
import ExportTool from "@/components/PanelTools/ExportTool.vue";
import PeriodTool from "@/components/PanelTools/PeriodTool.vue";
import ToolSeparator from "@/components/PanelTools/ToolSeparator.vue";

import { computed, onMounted, ref, shallowRef, ShallowRef, watch } from "vue";
import { BidTable } from "@/table";
import { BidViewer } from "@/viewer";

const props = defineProps({
	id: {
		type: Number,
		required: true,
	},
});

const emit = defineEmits<{
	(e: "notify", count: number, id: number): void;
}>();

const elementViewing = ref(false);

// Edit page
const viewer: ShallowRef<BidViewer | undefined> = shallowRef();

const table = new BidTable();
const fromDateString = ref("");
const toDateString = ref("");
const searchString = ref("");

table.filters.value = computed((): Array<(instance: any) => boolean> => {
	const periodFilter = (instance: any): boolean => {
		const rowDate = new Date(instance.create_date);
		const fromDate = new Date(fromDateString.value);
		const toDate = new Date(toDateString.value);

		return rowDate <= toDate && rowDate >= fromDate;
	};
	return [periodFilter];
}).value;
table.searcher.value = computed((): ((instance: any) => boolean) => {
	return (_: any): boolean => {
		return true;
	};
}).value;

const onRowClicked = (rowKey: number) => {
	viewer.value = new BidViewer(table.getModel(rowKey));
	elementViewing.value = true;
};
const loadTable = async (silent: boolean = false) => {
	await table.loadAll(silent);
	setTimeout(loadTable, 20000, true);
};
watch(table.highlightedCount, () => {
	emit("notify", table.highlightedCount.value, props.id);
});
onMounted(async () => {
	await loadTable();
});
</script>
<style scoped>
.bid-content {
	height: 100%;
	display: flex;
	flex-direction: column;
	gap: 30px;
}
.header-content {
	padding-top: 20px;
	padding-right: 20px;
	display: flex;
	align-items: center;
	flex-direction: row;
	overflow: hidden;
	flex-shrink: 0;
}
.header-content h1 {
	font-family: Stolzl;
	font-size: 36px;
	font-weight: 550;
	margin: 0;
}
.top-tools {
	margin-left: auto;
}
.view-panel-element-wrapper {
	display: flex;
	flex-direction: column;
}
</style>
