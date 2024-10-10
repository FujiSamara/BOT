<template>
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					<th>
						<div class="table-head">
							<div class="table-actions">
								<clickable-icon
									class="icons"
									style="width: 34px; margin-right: 15px"
									img-src="/img/backward.svg"
									@click="emit('close')"
								></clickable-icon>
								<clickable-icon
									v-if="canDelete"
									class="icons"
									img-src="/img/trash.svg"
									@click="emit('delete')"
								></clickable-icon>
								<clickable-icon
									v-if="canApprove"
									class="icons"
									img-src="/img/check.svg"
									:with-filter="false"
									@click="emit('approve')"
								>
								</clickable-icon>
								<clickable-icon
									v-if="canReject"
									class="icons"
									img-src="/img/reject.svg"
									:with-filter="false"
									@click="modalVisible = true"
								></clickable-icon>
							</div>
							<p style="margin: 0">Раздел</p>
						</div>
					</th>
					<th>Информация</th>
				</tr>
			</thead>
			<tbody>
				<tr v-for="field in props.viewer.fields">
					<th>{{ field.header }}</th>
					<th>
						<ul class="table-cell">
							<li
								class="table-cell-line"
								v-for="(cellLine, cellLineIndex) in field.cellLines"
							>
								<p v-if="cellLine.href.length > 0">
									<a
										@click.stop="
											async () => await onHrefClicked(cellLine.value)
										"
										class="link"
										>{{ cellLine.value }}</a
									>
									<span
										@click.stop="() => onExpandClicked(field, cellLineIndex)"
										v-if="cellLine.isImage"
										class="expand"
									></span>
								</p>
								<p v-if="cellLine.href.length === 0">{{ cellLine.value }}</p>
							</li>
						</ul>
					</th>
				</tr>
			</tbody>
		</table>

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
	</div>
</template>
<script setup lang="ts">
import ModalWindow from "@/components/ModalWindow.vue";
import DocumentView from "@/components/DocumentView.vue";
import type { Viewer } from "@/viewer";
import { Ref, ref, type PropType } from "vue";
import { BaseSchema, DocumentSchema } from "@/types";
import { useNetworkStore } from "@/store/network";
import { Cell } from "@/table";

const props = defineProps({
	viewer: {
		type: Object as PropType<Viewer<BaseSchema>>,
		required: true,
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

const modalVisible = ref(false);
const rejectReason = ref("");
const networkStore = useNetworkStore();

const documentViewVisible = ref(false);
const documents: Ref<Array<DocumentSchema>> = ref([]);
const initialDocumentIndex: Ref<number> = ref(1);

const emit = defineEmits(["delete", "approve", "reject", "close"]);

const onRejectCommentSubmit = () => {
	modalVisible.value = false;
	emit("reject", rejectReason.value);
	rejectReason.value = "";
};
const onHrefClicked = async (filename: string) => {
	await networkStore.downloadFile(filename);
};
const onExpandClicked = (cell: Cell, index: number) => {
	const docs = [];
	for (const [i, cellLine] of cell.cellLines.entries()) {
		if (cellLine.isImage) {
			if (index === i) {
				initialDocumentIndex.value = docs.length;
			}
			docs.push({ name: cellLine.value, href: cellLine.href });
		}
	}
	documentViewVisible.value = true;
	documents.value = docs;
};
</script>
<style scoped>
/*#region Table */
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
	width: 100%;
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
	width: 100%;
}
/*#endregion Table */

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
	padding-top: 20px;

	color: #ffffff;
	background-color: #993ca6;
	user-select: none;
}

thead th p {
	font-weight: 600;
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
	min-width: fit-content;
	text-align: center;
	position: relative;
}

.highlighted {
	background-color: #fdf7fd;
}

.table-head {
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: center;
}

.table-actions {
	position: absolute;
	filter: brightness(0) saturate(100%) invert(100%) sepia(7%) saturate(3904%)
		hue-rotate(245deg) brightness(117%) contrast(105%);
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: center;

	left: 20px;
	gap: 10px;
}

.icons {
	width: 17px;
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
</style>
