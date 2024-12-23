<script setup lang="ts">
import { PropType, ref } from "vue";
import { Table } from "@/components/table";
import { BaseSchema } from "@/types";

import PulseSpinner from "@/components/UI/PulseSpinner.vue";

const props = defineProps({
	table: {
		type: Object as PropType<Table<BaseSchema>>,
		required: true,
	},
});

const loading = ref(false);

const onClick = async () => {
	loading.value = true;
	await props.table.export();
	loading.value = false;
};
</script>

<template>
	<button @click="onClick" class="export-button">
		<div class="tool-icon-wrapper">
			<Transition name="fade">
				<PulseSpinner v-if="loading" class="spinner"></PulseSpinner>
			</Transition>
			<Transition name="fade">
				<img v-if="!loading" src="@/assets/icons/excel.svg" />
			</Transition>
		</div>
		<span>Выгрузить в Excel</span>
	</button>
</template>

<style scoped lang="scss">
.export-button {
	@include field;

	span {
		color: $fuji-green;
	}

	border-color: $fuji-green;

	&:hover,
	&.active {
		background-color: $fuji-green;
		border-color: $fuji-green;

		span {
			color: $fuji-white;
		}
	}
}
</style>
