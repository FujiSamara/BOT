<script setup lang="ts">
import { BaseEntity, SelectType } from ".";
import { PropType } from "vue";
import { computed } from "@vue/reactivity";
import MultiSelectInput from "@/components/MultiSelectInput.vue";
import MonoSelectInput from "../MonoSelectInput.vue";

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
const entity = props.entity;

const error = computed(() => {
	if (
		entity.entitiesList.value.length - entity.selectedEntities.value.length ===
			0 &&
		entity.formattedField.value.length !== 0 &&
		!entity.loading.value
	) {
		return "";
	}
	return undefined;
});
</script>

<template>
	<MultiSelectInput
		v-if="props.selectType === SelectType.MultiSelectInput"
		:error="error"
		:placeholder="entity.placeholder"
		:searchList="entity.entitiesList.value"
		:search-value="entity.formattedField.value"
		@submit="(val) => (entity.formattedField.value = val)"
		@select="(index: number) => entity.select(index)"
	></MultiSelectInput>
	<MonoSelectInput
		v-if="props.selectType === SelectType.MonoSelectInput"
		:error="error"
		:placeholder="entity.placeholder"
		:searchList="entity.entitiesList.value.map((val) => val.value)"
		:search-value="entity.formattedField.value"
		@submit="(val) => (entity.formattedField.value = val)"
		@select="(index: number) => entity.select(index)"
	>
	</MonoSelectInput>
</template>

<style scoped lang="scss"></style>
