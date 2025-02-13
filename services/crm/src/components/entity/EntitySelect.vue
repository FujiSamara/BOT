<script setup lang="ts">
import { PropType } from "vue";
import { BaseEntity, SelectType } from "@/components/entity";
import MultiEntitySelect from "@/components/entity/MultiEntitySelect.vue";
import MonoEntitySelect from "@/components/entity/MonoEntitySelect.vue";
import InputEntity from "@/components/entity/InputEntity.vue";
import DocumentEntitySelect from "@/components/entity/DocumentEntitySelect.vue";
import DateEntitySelect from "@/components/entity/DateEntitySelect.vue";
import TimeEntity from "@/components/entity/TimeEntity.vue";
import BoolEntitySelect from "@/components/entity/BoolEntitySelect.vue";

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
const defaultInput = props.selectType === SelectType.Input;
const monoDocumentSelect = props.selectType === SelectType.MonoDocument;
const multiDocumentSelect = props.selectType === SelectType.MultiDocument;
const dateSelect = props.selectType === SelectType.Date;
const timeSelect = props.selectType === SelectType.Time;
const checkboxSelect = props.selectType === SelectType.Checkbox;
</script>

<template>
	<div class="e-select">
		<MultiEntitySelect v-if="multiSelect" :entity="entity"></MultiEntitySelect>
		<MonoEntitySelect v-if="monoSelect" :entity="entity"></MonoEntitySelect>
		<InputEntity v-if="defaultInput" :entity="entity"></InputEntity>
		<DocumentEntitySelect
			v-if="monoDocumentSelect || multiDocumentSelect"
			:only-one="monoDocumentSelect"
			:entity="entity"
		></DocumentEntitySelect>
		<!--TODO: complete-->
		<DateEntitySelect v-if="dateSelect" :entity="entity"></DateEntitySelect>
		<TimeEntity v-if="timeSelect" :entity="entity"></TimeEntity>
		<BoolEntitySelect v-if="checkboxSelect" :entity="entity"></BoolEntitySelect>
	</div>
</template>

<style scoped lang="scss"></style>
