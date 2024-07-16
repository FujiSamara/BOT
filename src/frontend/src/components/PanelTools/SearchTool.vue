<template>
	<div class="search-tool-wrapper">
		<input placeholder="Поиск" v-model="value" />
		<img src="/img/search.svg" />
	</div>
</template>
<script setup lang="ts">
const value = defineModel("value", {
	type: String,
	required: true,
});
</script>
<style scoped>
.search-tool-wrapper {
	display: flex;
	flex-direction: row;
}

input {
	border: none;
	outline: none;
	font-family: Stolzl;
	font-size: 18px;
	color: #7f7f7f;
	width: 170px;
	caret-color: transparent;
}
</style>
