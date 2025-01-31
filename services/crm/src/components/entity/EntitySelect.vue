<script setup lang="ts">
import { BaseEntity, SelectType } from ".";
import { PropType } from "vue";
import MultiEntitySelect from "./MultiEntitySelect.vue";
import MonoEntitySelect from "./MonoEntitySelect.vue";

const props = defineProps({
	entity: {
		type: Object as PropType<BaseEntity<any>>,
		required: true,
	},
	selectType: {
		type: Number as PropType<SelectType>,
		required: true,
	},
});
const entity = props.entity as any;

const multiSelect = props.selectType === SelectType.MultiSelectInput;
const monoSelect = props.selectType === SelectType.MonoSelectInput;
</script>

<template>
	<div class="e-select">
		<MultiEntitySelect v-if="multiSelect" :entity="entity"></MultiEntitySelect>
		<MonoEntitySelect v-if="monoSelect" :entity="entity"></MonoEntitySelect>
	</div>
</template>

<style scoped lang="scss"></style>
