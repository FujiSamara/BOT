<script setup lang="ts">
import { Ref, ref, watch } from "vue";
import { Table } from "@/components/table";
import { BaseSchema } from "@/types";

const props = defineProps({
	table: {
		type: Table<BaseSchema>,
		required: true,
	},
	style: {
		type: String,
	},
});

const menuVisible = ref(false);
const headersHidden: Ref<Array<boolean>> = ref([]);
const oneColumnVisible = ref(false);

const checkboxClicked = (index: number) => {
	if (oneColumnVisible.value && !headersHidden.value[index]) {
		return;
	}

	const result = [...headersHidden.value];

	result[index] = !result[index];

	headersHidden.value = result;
};

watch(props.table.orderedHeaders, () => {
	headersHidden.value = props.table.orderedHeaders.value.map(() => false);
});

watch(headersHidden, () => {
	const hiddenHeaders = props.table.orderedHeaders.value.filter(
		(_, index) => headersHidden.value[index],
	);

	props.table.columnHidden.value = hiddenHeaders;

	oneColumnVisible.value =
		props.table.columnHidden.value.length ===
		props.table.orderedHeaders.value.length - 1;
});
</script>

<template>
	<div class="column-filter">
		<button
			@click="menuVisible = !menuVisible"
			:class="{ active: menuVisible }"
			:style="props.style"
			class="cf-switch"
		>
			<div class="tool-icon-wrapper">
				<div class="tool-icon filter"></div>
			</div>
			<span>Фильтр</span>
		</button>
		<Transition name="fade">
			<ul class="cf-menu" v-if="menuVisible">
				<li
					v-for="(header, index) in props.table.orderedHeaders.value"
					:key="header"
				>
					<div
						class="checkbox"
						:class="{
							checked: !headersHidden[index],
							disabled: oneColumnVisible,
						}"
						@click="() => checkboxClicked(index)"
					>
						<div class="icon"></div>
					</div>
					<p>{{ header }}</p>
				</li>
			</ul>
		</Transition>
	</div>
</template>

<style scoped lang="scss">
.column-filter {
	position: relative;

	.cf-switch {
		@include field;

		&.active {
			background-color: $fuji-blue;

			span {
				color: white;
			}

			.tool-icon-wrapper {
				.tool-icon {
					color: white;
				}
			}
		}

		.tool-icon-wrapper {
			.tool-icon {
				width: 15px;
				height: 10px;

				&.filter {
					mask-image: url("@/assets/icons/filter.svg");
				}
			}
		}
	}

	.cf-menu {
		display: flex;
		flex-direction: column;
		align-items: center;

		width: 202px;
		margin: 0;

		position: absolute;
		z-index: 1;

		gap: 16px;

		border-radius: 8px;
		list-style: none;
		padding: 24px;
		border: 1px solid $border-color;
		background-color: $table-bg-color;

		transition: opacity 0.5s;

		li {
			display: flex;
			flex-direction: row;

			width: 100%;

			p {
				margin: 0;
			}

			gap: 16px;

			.checkbox {
				@include checkbox;

				&.disabled.checked {
					background-color: $disabled-bg-color;
				}
			}
		}
	}
}
</style>
