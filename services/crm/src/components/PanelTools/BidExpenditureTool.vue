<template>
	<div class="wrapper">
		<border-input
			id="bid-select"
			placeholder="По статьям"
			class="input"
			v-model:value="field.formattedField.value"
			@focusin="inputFocused = true"
			@focusout="inputFocused = false"
		></border-input>
		<div class="list-wrapper">
			<Transition>
				<select-list
					v-show="
						field.selectList.value.length > 0 &&
						inputFocused &&
						!selectListVisible
					"
					:selectList="field.selectList.value"
					@select="onSelect"
				></select-list>
			</Transition>
		</div>
		<ClickableIcon
			v-if="selectList.length !== 0"
			class="icon"
			img-src="/img/filter.svg"
			@click="selectListVisible = !selectListVisible"
		></ClickableIcon>
		<div class="list-wrapper">
			<Transition>
				<SelectList
					@select="onClick"
					class="list"
					v-if="selectListVisible"
					:select-list="selectList"
				></SelectList>
			</Transition>
		</div>
	</div>
</template>
<script setup lang="ts">
import { Ref, ref } from "vue";
import SelectList from "@/components/UI/SelectList.vue";
import BorderInput from "@/components/UI/BorderInput.vue";
import ClickableIcon from "@/components/UI/ClickableIcon.vue";
import { FilterSchema } from "@/table";
import { ExpenditureSmartField } from "@/editor";

const props = defineProps({
	group: {
		type: Number,
		required: true,
	},
});
const filters = defineModel("filters", {
	type: Array<FilterSchema>,
	required: true,
});

const selectList: Ref<Array<string>> = ref([]);
const rawSelectList: Ref<Array<string>> = ref([]);
const selectListVisible: Ref<boolean> = ref(false);
const inputFocused = ref(false);
const field = new ExpenditureSmartField("Статья", "expenditure");

const onSelect = (index: number) => {
	field.applySelection(index);
	selectList.value.push(field.formattedField.value);
	rawSelectList.value.push(field.rawValue);
	filters.value.push({
		column: "expenditure",
		value: "",
		groups: [props.group],
		dependencies: [{ column: "name", value: field.rawValue.name }],
	});
	field.formattedField.value = "";
};
const onClick = (index: number) => {
	selectList.value.splice(index, 1);
	rawSelectList.value.splice(index, 1);
	filters.value.splice(index, 1);
	if (selectList.value.length === 0) {
		selectListVisible.value = false;
	}
};
</script>
<style scoped>
.input {
	background-color: #f6f6f6;
	margin-bottom: 0;
	color: #292929;
	z-index: 1;
}
.wrapper {
	display: flex;
	gap: 10px;
}
.icon {
	width: 20px;
}
.list-wrapper {
	position: absolute;
	top: 100%;
	display: flex;
	min-width: 200px;
	z-index: 2;
	background-color: #ffffff;
}

.v-enter-active,
.v-leave-active {
	transition: all 0.5s ease;
}

.v-enter-from,
.v-leave-to {
	max-height: 0;
}
</style>
