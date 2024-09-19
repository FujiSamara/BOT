<template>
	<div class="bid-content">
		<div v-if="!editingElement" class="header-content">
			<h1>Заявки</h1>
			<PanelTools class="top-tools">
				<PeriodTool
					v-model:from-date="fromDateString"
					v-model:to-date="toDateString"
				></PeriodTool>
				<ToolSeparator></ToolSeparator>
				<SeacrhTool
					id="topDepartmentSearch"
					placeholder="Производство"
					@input="(val) => (departmentSearchString = val)"
				></SeacrhTool>
				<SeacrhTool
					id="topSearch"
					@input="(val) => (searchString = val)"
				></SeacrhTool>
				<ToolSeparator></ToolSeparator>
				<ExportTool :callback="table.export.bind(table)"></ExportTool>
			</PanelTools>
		</div>
		<PanelTable
			v-if="!elementViewing"
			:table="table"
			:can-delete="true"
			:can-approve="true"
			:can-reject="true"
			@click="onRowClicked"
		></PanelTable>
		<ViewPanelRow
			v-if="elementViewing"
			@close="elementViewing = false"
			@approve="onApprove"
			@reject="onReject"
			@delete="onDelete"
			:canApprove="true"
			:canReject="true"
			:can-delete="true"
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

import { Ref, ref, shallowRef, ShallowRef, watch } from "vue";
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

const editingElement = ref(false);

const table = new BidTable();
const fromDateString = ref("");
const toDateString = ref("");

const elementViewing = ref(false);

const viewer: ShallowRef<BidViewer | undefined> = shallowRef();
const viewingIndex: Ref<number> = ref(-1);

const departmentSearchString = ref("");
const searchString = ref("");

watch([departmentSearchString, searchString], () => {
	const result = [];

	if (departmentSearchString.value.length > 3) {
		result.push({
			column: "department",
			term: departmentSearchString.value,
			groups: [0, 1],
		});
	}

	if (searchString.value.length > 3) {
		result.push(
			{
				column: "worker",
				term: searchString.value,
				groups: [0],
			},
			{
				column: "expenditure",
				term: searchString.value,
				groups: [1],
			},
		);
	}

	table.searchQuery.value = result;
});

watch([fromDateString, toDateString], () => {
	const fromDate = new Date(fromDateString.value);
	const toDate = new Date(toDateString.value);

	table.byDate.value = {
		column: "create_date",
		start: fromDate,
		end: toDate,
	};
});

watch(table.notifies, () => {
	emit("notify", table.notifies.value, props.id);
});

const onDelete = async () => {
	await table.delete(viewingIndex.value, true);
	elementViewing.value = false;
};
const onApprove = async () => {
	await table.approve(viewingIndex.value, true);
	elementViewing.value = false;
};
const onReject = async (reason: string) => {
	await table.reject(viewingIndex.value, true, reason);
	elementViewing.value = false;
};
const onRowClicked = (rowKey: number) => {
	viewer.value = new BidViewer(table.getModel(rowKey));
	elementViewing.value = true;
	viewingIndex.value = rowKey;
};
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
.edit-panel-element-wrapper {
	height: 100%;
	display: flex;
	flex-direction: column;
	padding-top: 56px;
	padding-bottom: 56px;
}
</style>
