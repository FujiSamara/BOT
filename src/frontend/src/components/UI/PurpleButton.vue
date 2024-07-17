<template>
	<button class="button">
		<slot></slot>
	</button>
</template>
<script>
export default {
	name: "purple-button",
};
</script>
<style scoped>
.button {
	height: 54px;
	padding: 10px;
	border-radius: 100px;
	border: none;
	background-color: #993ca6;
	color: #ffffff;
	font-family: benzin-regular;
	font-size: 14px;
	font-weight: 400;
	transition: 0.5s;
	-webkit-transition: 0.5s;
}
.button:hover {
	transform: scale(1.02);
	-webkit-transition: 0.5s;
	transition: 0.5s;
}
</style>
