<template>
	<div class="bid-content">
		<div v-show="!editingElement" class="header-content">
			<h1>Мои заявки</h1>
			<PanelTools class="top-tools">
				<BidExpenditureTool
					v-model:filters="expenditureFilters"
					:group="1"
				></BidExpenditureTool>
				<ToolSeparator></ToolSeparator>
				<BidStatusTool
					v-model:filters="statusFilters"
					:group="0"
				></BidStatusTool>
				<ToolSeparator></ToolSeparator>
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
			v-show="!elementViewing && !editingElement"
			:table="table"
			:can-delete="false"
			:can-create="true"
			:can-approve="false"
			:can-reject="false"
			@click="onRowClicked"
			@create="onCreateClicked"
		></PanelTable>

		<ViewPanelRow
			v-if="elementViewing"
			@close="elementViewing = false"
			@delete="onDelete"
			:canApprove="false"
			:canReject="false"
			:can-delete="false"
			:viewer="viewer!"
			class="view-page"
		></ViewPanelRow>
		<div v-if="editingElement" class="edit-panel-element-wrapper">
			<EditPanelRow
				class="edit-page"
				:editor="editor"
				@submit="onSubmit"
				@close="editingElement = false"
			></EditPanelRow>
		</div>
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
import { MyBidTable } from "@/table";
import { BidViewer } from "@/viewer";
import EditPanelRow from "@/components/EditPanelRow.vue";
import { BidEditor } from "@/editor";
import BidStatusTool from "@/components/PanelTools/BidStatusTool.vue";
import BidExpenditureTool from "@/components/PanelTools/BidExpenditureTool.vue";

const props = defineProps({
	id: {
		type: Number,
		required: true,
	},
});

const emit = defineEmits<{
	(e: "notify", count: number, id: number): void;
}>();

const table = new MyBidTable();

const fromDateString = ref("");
const toDateString = ref("");

const elementViewing = ref(false);

const viewer: ShallowRef<BidViewer | undefined> = shallowRef();
const viewingIndex: Ref<number> = ref(-1);

const departmentSearchString = ref("");
const searchString = ref("");

// Edit page
const editingElement = ref(false);
const editor: ShallowRef<BidEditor> = shallowRef(new BidEditor());
const editingElementKey: Ref<number> = ref(-1);

const onSubmit = async () => {
	if (editingElementKey.value !== -1) {
		await table.update(editor.value.toInstanse(), editingElementKey.value);
	} else {
		await table.create(editor.value.toInstanse());
	}
	editingElement.value = false;
};

watch([departmentSearchString, searchString], () => {
	const result = [];

	if (departmentSearchString.value.length > 3) {
		result.push({
			column: "department",
			term: departmentSearchString.value,
			groups: [0, 1, 2],
		});
	}

	if (searchString.value.length > 0) {
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
			{
				column: "id",
				term: searchString.value,
				groups: [2],
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

// Filters
const expenditureFilters = ref([]);
const statusFilters = ref([]);
table.filterQuery = computed(() => {
	return [...statusFilters.value, ...expenditureFilters.value];
});

const onDelete = async () => {
	await table.delete(viewingIndex.value, true);
	elementViewing.value = false;
};
const onRowClicked = (rowKey: number) => {
	viewer.value = new BidViewer(table.getModel(rowKey));
	elementViewing.value = true;
	viewingIndex.value = rowKey;
};
const onCreateClicked = () => {
	editor.value = new BidEditor();
	editingElementKey.value = -1;
	editingElement.value = true;
};
onMounted(() => table.startUpdatingLoop());
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
	flex-shrink: 0;
	position: relative;
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
