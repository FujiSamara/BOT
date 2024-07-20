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
		<div class="inputs-wrapper">
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
