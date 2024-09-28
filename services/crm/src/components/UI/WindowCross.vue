<template>
	<div class="cross-wrapper" @click="$emit('click')">
		<div class="c"></div>
		<div class="c"></div>
	</div>
</template>
<script>
export default {
	name: "window-cross",
	emits: ["click"],
};
</script>
<style>
.cross-wrapper {
	width: 24px;
	height: 24px;
	display: flex;
	flex-shrink: 0;
	justify-content: center;
	align-items: center;
	position: relative;
	-webkit-transition: 0.5s;
	transition: 0.5s;
}
.cross-wrapper:hover {
	transform: rotate(90deg);
	-webkit-transition: 0.5s;
	transition: 0.5s;
}
.c {
	position: absolute;
	width: 2px;
	height: 100%;
	background-color: #993ca6;
}
.c:nth-child(1) {
	transform: rotate(45deg);
}
.c:nth-child(2) {
	transform: rotate(-45deg);
}
</style>
