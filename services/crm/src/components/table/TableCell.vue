<script setup lang="ts"></script>

<template>
	<div class="cell-wrapper">
		<slot></slot>
	</div>
</template>

<style scoped lang="scss">
.cell-wrapper {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: flex-start;

	width: 150px;

	overflow-x: hidden;
}
</style>
