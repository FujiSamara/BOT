<script setup lang="ts">
import { PropType } from "vue";
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
</script>

<template>
	<DropDownMenu :style="props.style" :align-right="props.alignRight">
		<template #title>
			<div class="tool-icon-wrapper"><div class="tool-icon filter"></div></div>
			<span>Фильтры</span>
		</template>
		<template #menu> </template>
	</DropDownMenu>
</template>

<style scoped lang="scss">
.tool-icon-wrapper {
	.tool-icon {
		width: 15px;
		height: 10px;

		&.filter {
			mask-image: url("@/assets/icons/filter.svg");
		}
	}
}
</style>
