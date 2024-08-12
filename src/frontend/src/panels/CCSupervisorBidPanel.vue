<template>
	<div class="bid-content">
		<div class="header-content">
			<h1>Заявки РЦЗ</h1>
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
			@click="onRowClicked"
			:table="table"
			:can-delete="true"
			:can-approve="true"
			:can-reject="true"
		></PanelTable>
		<ViewPanelRow
			v-if="elementViewing"
			@close="elementViewing = false"
			@approve="onApprove"
			@reject="onReject"
			@delete="onDelete"
			:canApprove="true"
			:canReject="true"
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

import {
	computed,
	onMounted,
	Ref,
	ref,
	shallowRef,
	ShallowRef,
	watch,
} from "vue";
import { CCSupervisorBidTable } from "@/table";
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
const viewingID: Ref<number> = ref(-1);

const table = new CCSupervisorBidTable();
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

const onDelete = async () => {
	await table.delete(viewingID.value);
};
const onApprove = async () => {
	await table.approve(viewingID.value);
	elementViewing.value = false;
};
const onReject = async (reason: string) => {
	await table.reject(viewingID.value, reason);
	elementViewing.value = false;
};
const onRowClicked = (rowKey: number) => {
	viewer.value = new BidViewer(table.getModel(rowKey));
	elementViewing.value = true;
	viewingID.value = rowKey;
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
