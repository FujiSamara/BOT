<script setup lang="ts">
import { BaseEntity, SelectType } from ".";
import { PropType } from "vue";
import { computed } from "@vue/reactivity";
import MultiSelectInput from "@/components/selects/MultiSelectInput.vue";
import MonoSelectInput from "@/components/selects/MonoSelectInput.vue";

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
		entity.formattedField.value.length &&
		entity.formattedField.value.length < entity.neededWord
	) {
		return `Необходимо минимум ${entity.neededWord} символа`;
	}
	if (entity.notFound.value) {
		return "Совпадения не найдены";
	}

	return undefined;
});
</script>

<template>
	<div class="e-select">
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
			@close="() => entity.restoreSaved()"
			:required="entity.required"
		>
		</MonoSelectInput>
	</div>
</template>

<style scoped lang="scss"></style>
