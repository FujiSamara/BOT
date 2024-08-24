<template>
	<purple-button class="button-wrapper">
		<p style="margin: 0">Выгрузить в Excel</p>
		<img src="/img/export.svg" />
	</purple-button>
</template>
<script setup lang="ts"></script>
<!-- TODO: Make export callback -->
<style scoped>
.button-wrapper {
	width: 250px;
	height: 48px;
	background-color: #f5ecf6;
	color: #993ca6;
	font-size: 17px;
	font-family: Stolzl;
	font-weight: 550;

	display: flex;
	flex-direction: row;
	justify-content: center;
	align-items: center;
	gap: 8px;
}
p {
	margin: 0;
}
img {
	margin: 0;
}
</style>
