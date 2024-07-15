<template>
	<div class="edit-panel-wrapper">
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
</template>
<script setup lang="ts">
import { ref, Ref } from "vue";

const props = defineProps({
	inputHeaders: {
		type: Array<string>,
		required: true,
	},
});
const inputs: Array<Ref<string>> = props.inputHeaders.map(() => ref(""));
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
	width: fit-content;
	gap: 15px;
}
.input-wrapper {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: flex-start;
	width: fit-content;
	gap: 10px;
}
.input {
	background-color: #f6f6f6;
	width: 725px;
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
</style>
