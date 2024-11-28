<template>
	<div class="table-content-wrapper">
		<div class="table-wrapper">
			<table>
				<thead>
					<tr>
						<th>
							<div class="table-tools">
								<table-checkbox
									v-model:checked="props.table.allChecked.value"
									class="checkbox"
									id="main"
								></table-checkbox>
								<div class="table-actions">
									<clickable-icon
										v-show="props.table.anyChecked.value"
										v-if="canDelete"
										class="icons"
										img-src="/img/trash.svg"
										@click="onDelete"
									></clickable-icon>
									<clickable-icon
										v-show="!props.table.anyChecked.value"
										v-if="canCreate"
										class="icons"
										img-src="/img/add-plus.svg"
										@click="emit('create')"
										style="filter: none !important"
									></clickable-icon>
									<clickable-icon
										v-show="props.table.anyChecked.value"
										v-if="canApprove"
										class="icons"
										img-src="/img/check.svg"
										:with-filter="false"
										@click="onApprove"
									>
									</clickable-icon>
									<clickable-icon
										v-show="props.table.anyChecked.value"
										v-if="canReject"
										class="icons"
										img-src="/img/reject.svg"
										:with-filter="false"
										@click="onReject"
									></clickable-icon>
								</div>
							</div>
						</th>
						<th
							v-for="columnName in props.table.rows.value.headers"
							:key="columnName"
						>
							<div class="table-header">
								<p
									v-if="!props.table.orderDisabled(columnName)"
									@click="props.table.order(columnName)"
									style="margin: 0"
								>
									{{ columnName }}
								</p>
								<p
									v-if="props.table.orderDisabled(columnName)"
									style="margin: 0; color: gray"
								>
									{{ columnName }}
								</p>
								<img
									v-if="props.table.ordered(columnName)"
									:class="{ rotated: props.table.desc.value }"
									src="/img/sort_icon.svg"
								/>
							</div>
						</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="(row, index) in table.rows.value.rows"
						:key="row.id"
						@click.prevent="$emit('click', index)"
						@mouseleave="table.highlighted.value[index].value = false"
						:class="{
							highlighted:
								table.checked.value[index].value ||
								table.highlighted.value[index].value,
						}"
						:style="{ backgroundColor: table.colors.value[index] }"
					>
						<th>
							<div class="table-tools">
								<table-checkbox
									:id="row.id.toString()"
									v-model:checked="table.checked.value[index].value"
									class="checkbox"
								></table-checkbox>
							</div>
						</th>
						<th v-for="(cell, columnIndex) in row.columns" :key="columnIndex">
							<ul class="table-cell">
								<li
									class="table-cell-line"
									v-for="(cellLine, cellLineIndex) in cell.cellLines"
								>
									<p
										:style="{ color: cellLine.color }"
										v-if="cellLine.href.length > 0"
									>
										<a
											@click.stop="async () => await onHrefClicked(cellLine)"
											class="link"
											>{{ cellLine.value }}</a
										>
										<span
											@click.stop="() => onExpandClicked(cell, cellLineIndex)"
											v-if="cellLine.isImage"
											class="expand"
										></span>
									</p>
									<p
										:style="{ color: cellLine.color }"
										v-if="cellLine.href.length === 0"
									>
										{{ cellLine.value }}
									</p>
								</li>
							</ul>
						</th>
					</tr>
					<tr>
						<th style="border: none"></th>
					</tr>
				</tbody>
			</table>
			<div v-if="table.isLoading.value" class="loader-space">
				<circle-loader></circle-loader>
			</div>
		</div>

		<Transition name="modal">
			<ModalWindow
				class="reject-modal"
				v-if="modalVisible"
				@close="modalVisible = false"
			>
				<div class="modal-form">
					<border-input
						placeholder="Причина отказа"
						v-model:value="rejectReason"
					></border-input>
					<purple-button
						class="modal-button"
						@click.prevent="onRejectCommentSubmit"
						><p style="margin: 0">Отказать</p></purple-button
					>
				</div>
			</ModalWindow>
		</Transition>

		<Suspense>
			<Transition name="modal">
				<DocumentView
					v-if="documentViewVisible"
					:documents="documents"
					:index="initialDocumentIndex"
					@close="documentViewVisible = false"
				></DocumentView>
			</Transition>
		</Suspense>

		<TablePagination
			v-model:currentPage="props.table.currentPage.value"
			:pageCount="props.table.pageCount.value"
		>
		</TablePagination>
	</div>
</template>
<script setup lang="ts">
import ClickableIcon from "@/components/UI/ClickableIcon.vue";
import ModalWindow from "@/components/ModalWindow.vue";
import TablePagination from "@/components/TablePagination.vue";
import DocumentView from "@/components/DocumentView.vue";
import type { Cell, CellLine, Table } from "@/table";
import { Ref, ref, type PropType } from "vue";
import { BaseSchema, DocumentSchema } from "@/type";
import { useNetworkStore } from "@/store/network";

const props = defineProps({
	table: {
		type: Object as PropType<Table<BaseSchema>>,
		required: true,
	},
	canCreate: {
		type: Boolean,
		required: false,
	},
	canDelete: {
		type: Boolean,
		required: false,
	},
	canApprove: {
		type: Boolean,
		required: false,
	},
	canReject: {
		type: Boolean,
		required: false,
	},
});

const networkStore = useNetworkStore();

const modalVisible = ref(false);
const rejectReason = ref("");

const documentViewVisible = ref(false);
const documents: Ref<Array<DocumentSchema>> = ref([]);
const initialDocumentIndex: Ref<number> = ref(1);

const emit = defineEmits(["click", "create", "delete", "approve", "reject"]);

const onDelete = async () => {
	await props.table.deleteChecked();
	emit("delete");
};
const onApprove = async () => {
	await props.table.approveChecked();
	emit("approve");
};
const onReject = () => {
	modalVisible.value = true;
};
const onRejectCommentSubmit = async () => {
	modalVisible.value = false;
	await props.table.rejectChecked(rejectReason.value);
	rejectReason.value = "";
	emit("reject");
};
const onHrefClicked = async (cellLine: CellLine) => {
	if (cellLine.forceHref) {
		await networkStore.downloadFile(cellLine.value, cellLine.href);
	} else {
		await networkStore.downloadFile(cellLine.value);
	}
};
const onExpandClicked = (cell: Cell, index: number) => {
	const docs: Array<DocumentSchema> = [];
	for (const [i, cellLine] of cell.cellLines.entries()) {
		if (cellLine.isImage) {
			if (index === i) {
				initialDocumentIndex.value = docs.length;
			}
			docs.push({ name: cellLine.value, href: cellLine.href, forceHref: true });
		}
	}
	documentViewVisible.value = true;
	documents.value = docs;
};
</script>
<style scoped>
.table-content-wrapper {
	gap: 10px;
	display: flex;
	flex-direction: column;
	min-height: 0;
	height: fit-content;
	flex-grow: 1;
	align-items: center;
	justify-content: space-between;
}

.table-wrapper {
	background-color: #ffffff;
	overflow-y: auto;
	overflow-x: auto;
	white-space: nowrap;
	overscroll-behavior: none;
	height: fit-content;

	border-radius: 20px;
	border: 1px solid #e6e6e6;
	max-width: 100%;
	width: min-content;
}

.table-wrapper::-webkit-scrollbar {
	width: 5px;
	height: 5px;
	border-radius: 2000px;
}

.table-wrapper::-webkit-scrollbar-track {
	background-color: #e7e7e7;
	margin: 20px;
}

.table-wrapper::-webkit-scrollbar-thumb:vertical,
.table-wrapper::-webkit-scrollbar-thumb:horizontal {
	height: 10px;
	width: 5px;
	height: 15px !important;
	border-radius: 22px;
	background-color: #993ca6;
}

table {
	height: fit-content;

	/** border */
	border-collapse: collapse;
	border-spacing: 0;
}

/** Cell border  */
tbody tr th {
	border-bottom: 1px solid #e6e6e6;
	border-right: 1px solid #e6e6e6;
}
tbody tr:first-child th {
	border-top: 1px solid #e6e6e6;
}

/** Empty up and down border */
tbody tr th:last-child {
	border-right: none;
}
tbody tr:last-child th {
	border-bottom: none;
}

/** Bottom row */
tbody tr:last-child th {
	padding: 10px;
}

/** Row selection */
tr:not(:last-child):hover {
	background-color: #fdf7fd !important;
}

/** Table head settings  */
thead tr th:first-child {
	border-top-left-radius: 20px;
}

thead tr th:last-child {
	border-top-right-radius: 20px;
}

thead {
	position: sticky;
	top: 0;
	left: 0;
	z-index: 1;
}

thead th {
	border: none;
	font-weight: 600;
	padding-bottom: 20px;
	padding-top: 30px;

	color: black;
	background-color: #ffffff;
	user-select: none;
}

thead th p:hover {
	text-decoration: underline;
	cursor: pointer;
}

thead th img {
	height: 8px;
}

.table-header {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 2px;
}

/** All cells */
th {
	padding: 20px;
	color: #7f7f7f;
	font-family: Stolzl;
	font-size: 15px;
	font-weight: 400;
	min-width: 60px;
	text-align: center;
	position: relative;
}

.highlighted {
	background-color: #fdf7fd !important;
}

.table-tools {
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: flex-start;
	gap: 20px;
}

.table-actions {
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: center;
	gap: 10px;
}

.icons {
	width: 20px;
}

.loader-space {
	display: flex;
	width: 100%;
	min-height: 70px;
	position: relative;
	justify-content: center;
}

/*#region Table cell */
.table-cell {
	padding: 0;
	margin: 0;
	cursor: pointer;
}
.table-cell-line {
	list-style-type: none;
}
.table-cell p {
	margin: 0;
	cursor: default;

	display: flex;
	align-items: center;
	gap: 8px;
}
.table-cell .link {
	color: #993ca6;
	transition: color 0.25s;
	text-decoration: underline;
	user-select: none;
	cursor: pointer;
}
.table-cell .link:hover {
	color: #7f7f7f;
	transition: color 0.25s;
}
.table-cell .expand {
	width: 20px;
	height: 20px;

	transition: color 0.25s;
	mask: url("/img/eye.svg");
	fill: currentColor;
	background-color: currentColor;
	cursor: pointer;
}
.table-cell .expand:hover {
	color: #993ca6;
	transition: color 0.25s;
}
/*#endregion */

/*#region Modal window */

/*#region Modal window transition */
.modal-enter-active,
.modal-leave-active {
	transition: opacity 0.5s ease;
}

.modal-enter-from,
.modal-leave-to {
	opacity: 0;
}
/*#endregion */

.modal-header {
	font-size: 24px;
}

.modal-form {
	display: flex;
	width: 90%;
	flex-direction: column;
	align-items: center;
	align-content: center;
	gap: 15px;
}

.modal-form input {
	width: 100%;
}

.modal-button {
	width: 100%;
}

.modal-button p {
	user-select: none;
}
/*#endregion */

.rotated {
	transform: rotate(180deg);
}
</style>
