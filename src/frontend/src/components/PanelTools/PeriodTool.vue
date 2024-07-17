<template>
	<div class="period-tool-wrapper">
		<p>Период:</p>
		<span>с</span>
		<input type="date" class="from-input" v-model="fromValue" />
		<span>по</span>
		<input type="date" class="to-input" v-model="toValue" />
	</div>
</template>
<script setup lang="ts">
import { onMounted } from "vue";

const fromValue = defineModel("fromDate", { type: String, required: true });

const toValue = defineModel("toDate", { type: String, required: true });

onMounted(() => {
	fromValue.value = "0001-01-01";
	toValue.value = "3001-01-01";
});
</script>
<style scoped>
.period-tool-wrapper {
	display: flex;
	flex-direction: row;
	gap: 10px;
	align-items: center;
	justify-content: center;
	background-color: transparent;
}

p {
	font-family: Stolzl;
	color: #292929;
	margin: 0;
	margin-right: 40px;
}
input {
	border-bottom: 1px solid #cccccc;
	background-color: transparent;
	border-top: none;
	border-left: none;
	border-right: none;

	outline: none;
	caret-color: transparent;
	font-family: Stolzl;
	font-size: 18px;
	color: #292929;
	display: flex;
	flex-direction: row;
	width: 81px;
	height: 18px;
}
span {
	color: #292929;
	font-size: 20px;
	font-family: Stolzl;
	opacity: 0.4;
}
input::-webkit-inner-spin-button,
input::-webkit-calendar-picker-indicator {
	display: none;
	-webkit-appearance: none;
}
</style>
