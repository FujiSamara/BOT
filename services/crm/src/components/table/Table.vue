<script setup lang="ts">
import {
	computed,
	nextTick,
	onMounted,
	PropType,
	ref,
	Ref,
	useTemplateRef,
	watch,
} from "vue";
import TableCellContainer from "@/components/table/TableCellContainer.vue";
import Checkbox from "@/components/UI/Checkbox.vue";
import { BaseSchema } from "@/types";
import { Table } from "@/components/table";
import { useRoute, useRouter } from "vue-router";

const props = defineProps({
	table: {
		type: Object as PropType<Table<BaseSchema>>,
		required: true,
	},
	blockLoading: {
		type: Boolean,
	},
});
const emits = defineEmits<{
	(e: "rowClick", index: number): void;
	(e: "cellClick", rowIndex: number, cellIndex: number): void;
}>();

const router = useRouter();
const route = useRoute();

const tableRef = useTemplateRef("table");
const photoOpenned = ref(false);

const resizeCells = () => {
	const cells = tableRef.value!.getElementsByClassName("t-cell");
	for (const cell of cells) {
		(cell as HTMLElement).style.width = "max-content";
	}

	const maxGrantedWidth = parseInt(
		window
			.getComputedStyle(document.documentElement)
			.getPropertyValue("--max-cell-width"),
	);
	const cellsWidth = [...titles.value.map(() => 0), 0];

	for (const cell of cells) {
		window.getComputedStyle(cell).opacity; // Force dom to rerender component.
		const id = parseInt(cell.id) + 1;
		if (cellsWidth[id] < (cell as HTMLElement).offsetWidth) {
			cellsWidth[id] = (cell as HTMLElement).offsetWidth;
		}
	}

	for (let index = 0; index < cellsWidth.length; index++) {
		const cellWidth = cellsWidth[index];

		if (cellWidth > maxGrantedWidth) {
			cellsWidth[index] = maxGrantedWidth;
		}
	}

	for (const cell of cells) {
		const id = parseInt(cell.id) + 1;

		(cell as HTMLElement).style.width = `${cellsWidth[id]}px`;
	}

	return cellsWidth;
};

const updateOrder = async () => {
	const query = { ...route.query };

	query["orderBy"] = props.table.orderBy.value;

	if (props.table.desc.value) {
		query["desc"] = "";
	} else if ("desc" in query) {
		delete query["desc"];
	}

	await router.replace({ query: query });
};
const loadOrder = () => {
	if ("orderBy" in route.query) {
		props.table.orderBy.value = route.query["orderBy"] as string;

		if ("desc" in route.query) props.table.desc.value = true;
		else props.table.desc.value = false;
	}
};

const loadTable = () => {
	props.table.blockLoop.value = false;
	props.table.forceRefresh();
};

const titles: Ref<string[]> = computed(() => {
	if (props.table.orderedHeaders.value.length || !titles.value) {
		return props.table.visibleHeaders.value;
	} else {
		return titles.value;
	}
});

const rows = computed(() => props.table.visibleRows.value);

watch([rows, tableRef], async () => {
	if (rows.value.length === 0 || tableRef.value === null) {
		return;
	}

	await nextTick();
	resizeCells();
});

watch([props.table.orderBy, props.table.desc], updateOrder);

onMounted(() => {
	loadOrder();
});
</script>

<template>
	<div class="table" ref="table">
		<Transition name="fade">
			<div
				@click="if (!props.blockLoading) loadTable();"
				class="load-button"
				v-if="props.table.blockLoop.value"
				:class="{ disabled: props.blockLoading }"
			>
				<div class="tool-icon-wrapper">
					<div class="tool-icon search"></div>
				</div>
				<span>Загрузить</span>
			</div>
		</Transition>
		<TransitionGroup
			name="shift"
			tag="div"
			style="display: inline-block; width: fit-content"
			:duration="{ enter: 1500, leave: 500 }"
		>
			<div class="t-row titles" v-if="titles.length !== 0" :key="-1">
				<TableCellContainer id="-1" class="t-cell check">
					<Checkbox
						:checked="props.table.allChecked.value"
						@click="
							props.table.allChecked.value = !props.table.allChecked.value
						"
					>
					</Checkbox>
				</TableCellContainer>
				<TableCellContainer
					:id="index"
					class="t-cell"
					v-for="(title, index) in titles"
					:key="title"
				>
					<div
						class="title"
						@click="
							if (!props.table.orderDisabled(title)) props.table.order(title);
						"
						:class="{
							lock: props.table.orderDisabled(title),
						}"
					>
						<p :style="{ color: props.table.getHeaderColor(title) }">
							{{ title }}
						</p>
						<Transition name="fade">
							<div
								class="icon"
								:class="{
									reversed:
										props.table.desc.value && !props.table.orderDisabled(title),
								}"
								v-show="
									props.table.ordered(title) || props.table.orderDisabled(title)
								"
							></div>
						</Transition>
					</div>
				</TableCellContainer>
			</div>
			<div
				class="t-row"
				v-for="(row, index) in rows"
				:key="row.id"
				@click="emits('rowClick', index)"
			>
				<TableCellContainer id="-1" class="t-cell check">
					<Checkbox
						:checked="table.checked.value[index].value"
						@click="
							table.checked.value[index].value =
								!table.checked.value[index].value
						"
					>
					</Checkbox>
				</TableCellContainer>
				<TableCellContainer
					:id="cellIndex"
					class="t-cell"
					v-for="(cell, cellIndex) in row.columns"
					:key="cellIndex"
					:cell="cell"
					@click="emits('cellClick', index, cellIndex)"
					@photo-open="photoOpenned = true"
					@photo-close="photoOpenned = false"
					:photo-disabled="photoOpenned"
				>
				</TableCellContainer>
			</div>
		</TransitionGroup>
	</div>
</template>

<style scoped lang="scss">
.table {
	display: flex;
	flex-direction: column;

	flex-grow: 1;

	margin: 0;

	padding: 0 16px;
	border-radius: 16px;

	overflow-x: auto;

	background-color: $main-white;

	.load-button {
		@include field;

		width: 200px;
		height: 48px;

		margin: auto;

		.tool-icon-wrapper {
			.tool-icon {
				&.search {
					mask-image: url("@/assets/icons/loop.svg");
					color: $main-dark-gray;
				}
			}
		}

		&:hover,
		&.active {
			.tool-icon-wrapper {
				.tool-icon {
					&.search {
						color: $main-accent-blue;
					}
				}
			}
		}
	}

	.t-row {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 32px;
		height: var(--row-height);
		min-height: var(--row-height);
		max-height: var(--row-height);
		width: fit-content;

		border-radius: 8px;
		border: 1px solid transparent;

		padding: 8px 24px;

		font-size: 14px;
		font-family: Wix Madefor Display;
		font-weight: 500;
		line-height: 17.64px;
		color: $main-accent-blue;

		transition: border-color 0.25s;

		&.titles {
			font-size: 16px;
			line-height: 20.16px;

			height: 84px;
			min-height: 84px;
			max-height: 84px;

			.t-cell {
				white-space: nowrap;
			}

			.title {
				display: flex;
				flex-direction: row;
				align-items: center;
				gap: 16px;

				cursor: pointer;

				p {
					margin: 0;
				}

				.icon {
					@include arrow();

					transition:
						transform 0.25s,
						opacity 0.5s ease;
				}

				&.lock {
					cursor: not-allowed;
					.icon {
						width: 7px;
						height: 9px;
						mask: url("@/assets/icons/lock.svg") no-repeat;
					}
				}
			}
		}

		&:nth-child(even) {
			background-color: $bg-accent-blue-3;
		}

		.check {
			width: fit-content;
		}

		&:not(:first-child):hover {
			border-color: $sec-active-blue;
			background-color: $sec-active-blue-10;
		}
	}
}
</style>
