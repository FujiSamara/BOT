<template>
	<form class="edit-panel-wrapper" @submit.prevent="$emit('submit')">
		<div class="inputs-wrapper">
			<div
				class="input-wrapper"
				v-for="(field, _) in props.editor.fields"
				:key="field.name"
			>
				<p class="input-header">{{ field.name }}:</p>
				<border-input
					class="input"
					v-model:value="field.formattedField.value"
				></border-input>
			</div>
		</div>

		<purple-button class="button"
			><p style="margin: 0">Сохранить</p></purple-button
		>
	</form>
</template>
<script setup lang="ts">
import BorderInput from "./UI/BorderInput.vue";
import type { ExpenditureEditor } from "@/editor";
import type { PropType } from "vue";

const props = defineProps({
	editor: {
		type: Object as PropType<ExpenditureEditor>,
		required: true,
	},
});
const emit = defineEmits(["submit"]);
</script>
<style scoped>
.edit-panel-wrapper {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	justify-content: center;
	background-color: #ffffff;
	border-radius: 20px;
	width: 725px;
	max-height: 100%;
	padding-bottom: 18px;
	gap: 20px;
}
.inputs-wrapper {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	width: 100%;
	gap: 20px;
	overflow: auto;
	padding-left: 20px;
	padding-right: 20px;
	padding-top: 18px;
}
.inputs-wrapper::-webkit-scrollbar {
	width: 5px;
	height: 5px;
	border-radius: 2000px;
}

.inputs-wrapper::-webkit-scrollbar-track {
	background-color: #e7e7e7;
	margin-top: 20px;
}

.inputs-wrapper::-webkit-scrollbar-thumb:vertical {
	height: 10px;
	width: 5px;
	height: 15px !important;
	border-radius: 22px;
	background-color: #993ca6;
}
.input-wrapper {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: flex-start;
	width: 100%;
	gap: 10px;
}
.input {
	background-color: #f6f6f6;
	width: 100%;
	height: 48px;
	margin: 0;
	color: #292929;
}
.input-header {
	color: #292929;
	font-family: Stolzl;
	font-weight: 500;
	font-size: 18px;
	margin: 0;
}
.button {
	width: 100%;
	background-color: #f5ecf6;
	color: #993ca6;
	font-size: 17px;
}
</style>
