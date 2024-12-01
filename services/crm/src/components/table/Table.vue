<script setup lang="ts">
import { computed, nextTick, onMounted, useTemplateRef, watch } from "vue";
import TableCell from "@/components/table/TableCell.vue";
import { BaseSchema } from "@/types";
import { Table } from "@/components/table";

const props = defineProps({
	table: {
		type: Table<BaseSchema>,
		required: true,
	},
});

const tableRef = useTemplateRef("table");

const resizeTable = () => {
	const tableElement = tableRef.value as HTMLElement;
	const tableHeigth = tableElement.offsetHeight;

	const rowCount = Math.floor((tableHeigth - 72) / 64);

	props.table.rowsPerPage.value = rowCount;
};

const resizeCells = () => {
	const cells = tableRef.value!.getElementsByClassName("t-cell");
	for (const cell of cells) {
		(cell as HTMLElement).style.width = "fit-content";
	}

	const maxGrantedWidth = 150;
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

const titles = computed(() => props.table.headers.value);

const rows = computed(() => props.table.rows.value);

watch(rows, async () => {
	if (rows.value.length === 0) {
		return;
	}

	await nextTick();

	console.log(rows.value);

	resizeCells();
});

onMounted(() => {
	resizeTable();
});
</script>

<template>
	<div class="p-table" ref="table">
		<TransitionGroup
			name="table"
			tag="div"
			style="display: inline-block; width: fit-content"
		>
			<div class="t-row titles" v-if="titles.length !== 0" :key="-1">
				<TableCell id="-1" class="t-cell check">
					<div
						class="checkbox"
						:class="{ checked: props.table.allChecked.value }"
						@click="
							props.table.allChecked.value = !props.table.allChecked.value
						"
					>
						<div class="icon"></div>
					</div>
				</TableCell>
				<TableCell
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
				</TableCell>
			</div>
			<div class="t-row" v-for="(row, index) in rows" :key="row.id">
				<TableCell id="-1" class="t-cell check">
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
				</TableCell>
				<TableCell
					:id="index"
					class="t-cell"
					v-for="(column, index) in row.columns"
					:key="index"
					>{{ column.cellLines[0].value }}
				</TableCell>
			</div>
		</TransitionGroup>
	</div>
</template>

<style scoped lang="scss">
.p-table {
	display: flex;
	flex-direction: column;

	flex-grow: 1;

	margin: 0;

	padding: 0 16px;
	border-radius: 16px;

	overflow-x: auto;

	background-color: $table-background-color;

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

		padding: 0 24px;

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
					mask-size: contain;

					transition:
						transform 0.3s,
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
				display: flex;
				justify-content: center;
				align-items: center;

				width: 24px;
				height: 24px;
				padding: 7px 5px;
				border-radius: 6px;

				border: 1px $border-color solid;

				.icon {
					background-color: currentColor;
					width: 12px;
					height: 8px;
					fill: currentColor;

					mask: url("@/assets/icons/check.svg") no-repeat;
					mask-size: contain;

					color: $fuji-white;
				}

				transition:
					background-color 0.3s,
					border-color 0.3s;

				&.checked {
					background-color: $fuji-blue;
					border-color: transparent;
				}
			}
		}
	}

	// Transitions

	.table-item {
		display: inline-block;
		margin-right: 10px;
	}
	.table-enter-active,
	.table-leave-active {
		transition: all 1s ease;
	}
	.table-enter-from,
	.table-leave-to {
		opacity: 0;
		transform: translateY(30px);
	}

	.fade-enter-from,
	.fade-leave-to {
		opacity: 0;
	}
}
</style>
