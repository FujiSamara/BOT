<script setup lang="ts">
import { computed, nextTick, onMounted, Ref, useTemplateRef, watch } from "vue";
import TableCellContainer from "@/components/table/TableCellContainer.vue";
import { BaseSchema } from "@/types";
import { Table } from "@/components/table";
import { useRoute, useRouter } from "vue-router";

const props = defineProps({
	table: {
		type: Table<BaseSchema>,
		required: true,
	},
});

const router = useRouter();
const route = useRoute();

const tableRef = useTemplateRef("table");

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
		<TransitionGroup
			name="table"
			tag="div"
			style="display: inline-block; width: fit-content"
			:duration="{ enter: 1500, leave: 500 }"
		>
			<div class="t-row titles" v-if="titles.length !== 0" :key="-1">
				<TableCellContainer id="-1" class="t-cell check">
					<div
						class="checkbox"
						:class="{ checked: props.table.allChecked.value }"
						@click="
							props.table.allChecked.value = !props.table.allChecked.value
						"
					>
						<div class="icon"></div>
					</div>
				</TableCellContainer>
				<TableCellContainer
					:id="index"
					class="t-cell"
					v-for="(title, index) in titles"
					:key="title"
				>
					<div class="title" @click="props.table.order(title)">
						<p>{{ title }}</p>
						<Transition name="fade">
							<div
								class="icon"
								:class="{ reversed: props.table.desc.value }"
								v-show="props.table.ordered(title)"
							></div>
						</Transition>
					</div>
				</TableCellContainer>
			</div>
			<div class="t-row" v-for="(row, index) in rows" :key="row.id">
				<TableCellContainer id="-1" class="t-cell check">
					<div
						class="checkbox"
						:class="{ checked: table.checked.value[index].value }"
						@click="
							table.checked.value[index].value =
								!table.checked.value[index].value
						"
					>
						<div class="icon"></div>
					</div>
				</TableCellContainer>
				<TableCellContainer
					:id="index"
					class="t-cell"
					v-for="(cell, index) in row.columns"
					:key="index"
					:cell="cell"
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

	background-color: $table-bg-color;

	.t-row {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 32px;
		height: 64px;
		min-height: 64px;
		max-height: 64px;
		width: fit-content;

		border-radius: 8px;

		padding: 8px 24px;

		font-size: 14px;
		font-family: Wix Madefor Display;
		font-weight: 500;
		line-height: 17.64px;
		color: $text-color;

		&.titles {
			font-size: 16px;
			line-height: 20.16px;

			height: 72px;
			min-height: 72px;
			max-height: 72px;

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
					background-color: currentColor;
					width: 9px;
					height: 6px;
					fill: currentColor;

					mask: url("@/assets/icons/arrow.svg") no-repeat;

					transition:
						transform 0.25s,
						opacity 0.5s ease;

					&.reversed {
						transform: rotate(180deg);
					}
				}
			}
		}

		&:nth-child(even) {
			background-color: $row-bg-color;
		}

		.check {
			width: fit-content;

			.checkbox {
				@include checkbox;
			}
		}
	}

	// Transitions

	.table-enter-active,
	.table-leave-active {
		transition: all 1s ease;
	}
	.table-enter-from,
	.table-leave-to {
		opacity: 0;
		transform: translateY(30px);
	}
}
</style>
