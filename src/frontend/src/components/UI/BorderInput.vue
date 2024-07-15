<template>
	<input :placeholder="placeholder" v-model="value" />
</template>
<script setup>
const placeholder = defineModel("placeholder");
const value = defineModel("value");
</script>
<script>
export default {
	name: "border-input",
};
</script>
<style scoped>
input {
	border: 1px solid #e8e8e8;
	border-radius: 10px;
	height: 40px;
	padding: 10px 20px 10px 20px;
	-webkit-transition: 0.5s;
	transition: 0.5s;
}

input::placeholder {
	color: #d0d0d0;
	font-weight: 400;
	font-size: 18px;
	font-family: Stolzl;
}

input:focus {
	border-color: #c1c1c1;
	-webkit-transition: 0.5s;
	transition: 0.5s;
	outline: none;
}
</style>
