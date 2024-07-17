<template>
	<form
		class="edit-panel-wrapper"
		@submit.prevent="
			$emit(
				'submit',
				inputs.map((val) => val.value),
			)
		"
	>
		<div
			class="input-wrapper"
			v-for="(inputHeader, index) in props.inputHeaders"
			:key="inputHeader"
		>
			<p class="input-header">{{ inputHeader }}:</p>
			<border-input
				class="input"
				v-model:value="inputs[index].value"
			></border-input>
		</div>
		<purple-button class="button"
			><p style="margin: 0">Сохранить</p></purple-button
		>
	</form>
</template>
<script setup lang="ts">
import { ref, Ref } from "vue";
import BorderInput from "./UI/BorderInput.vue";

const props = defineProps({
	inputHeaders: {
		type: Array<string>,
		required: true,
	},
	defaultInputs: {
		type: Array<string>,
		required: false,
	},
});
const emit = defineEmits(["submit"]);

let inputs: Array<Ref<string>> = [];
if (
	!props.defaultInputs ||
	props.defaultInputs.length !== props.inputHeaders.length
) {
	inputs = props.inputHeaders.map(() => ref(""));
} else {
	inputs = props.defaultInputs.map((val) => ref(val));
}
</script>
<style scoped>
.edit-panel-wrapper {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	justify-content: center;
	padding: 18px 20px 18px 20px;
	background-color: #ffffff;
	border-radius: 20px;
	width: 725px;
	gap: 20px;
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
