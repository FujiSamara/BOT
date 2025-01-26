<script setup lang="ts">
import { PropType, Ref, ref, watch } from "vue";
import { Table } from "@/components/table";
import { BaseSchema } from "@/types";
import DropDownMenu from "@/components/DropDownMenu.vue";

const props = defineProps({
	table: {
		type: Object as PropType<Table<BaseSchema>>,
		required: true,
	},
	style: {
		type: String,
	},
	alignRight: {
		type: Boolean,
	},
});

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
	<DropDownMenu :style="props.style" :align-right="props.alignRight">
		<template #title>
			<div class="tool-icon-wrapper"><div class="tool-icon filter"></div></div>
			<span>Настройка столбцов</span>
		</template>
		<template #menu>
			<li
				class="menu-list"
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
		</template>
	</DropDownMenu>
</template>

<style scoped lang="scss">
.tool-icon-wrapper {
	.tool-icon {
		width: 15px;
		height: 10px;

		&.filter {
			mask-image: url("@/assets/icons/sort.svg");
		}
	}
}

.menu-list {
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
</style>
