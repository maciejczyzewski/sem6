// RESOURCE:
// https://github.com/trekhleb/state-of-the-art-shitcode

// MUSIC:
// https://www.youtube.com/watch?v=wuCK-oiE3rM
// https://www.youtube.com/watch?v=5_ARibfCMhw
// https://www.youtube.com/watch?v=FYwAg_bG9DI
// https://www.youtube.com/watch?v=XBf8L7Kkdeo
// https://www.youtube.com/watch?v=o1trtCtxJYY

import './App.css';

import star_full from './star-full.svg';
import star_empty from './star-empty.svg';
import help from './help.svg';
import doge from './doge.svg';

import React, { Component } from 'react';

// FIXME: repair this data!
// FIXME: add tutorial toolkit? (help?)

var DEMO_DATA = [
	{
		idx: 1,
		name: 'Thermal Physics test tomorrow. Wish me luck.',
		desc: '#physicsmemes',
		image:
			'https://preview.redd.it/ogvvnpnmvji31.jpg?width=640&crop=smart&auto=webp&s=1c0d23d491b7ec45977a8068553ef39770a6bce0',
		rating: 5,
		opacity: 1,
	},
	{
		idx: 2,
		name: 'Oof-size: large',
		desc: '#physicsmemes',
		image:
			'https://preview.redd.it/lsn1s3akgia41.jpg?width=640&crop=smart&auto=webp&s=2d88c1d549a8837a0437f5375536b4747e557747',
		rating: 4,
		opacity: 1,
	},
	{
		idx: 3,
		name: 'High iq meme',
		desc: '#physicsmemes',
		image:
			'https://preview.redd.it/xkax2cyhtbf41.jpg?width=640&crop=smart&auto=webp&s=b9a5e758957bd390852b60d0c4eedeb3ad7a3d98',
		rating: 1,
		opacity: 1,
	},
];

////////////////////////////////////////////////////////////////////////////////

// https://stackoverflow.com/questions/5717093/check-if-a-javascript-string-is-a-url
function validURL(str) {
	var pattern = new RegExp(
		'^(https?:\\/\\/)?' + // protocol
		'((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // domain name
		'((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
		'(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
		'(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
			'(\\#[-a-z\\d_]*)?$',
		'i',
	); // fragment locator
	return !!pattern.test(str);
}

class Button extends Component {
	handleClick = () => {
		console.log('this is:', this);
		this.props.handle(this);
	};

	render() {
		if (this.props.toggle === undefined) {
			return (
				<button className="button" onClick={this.handleClick}>
					{this.props.name}
				</button>
			);
		} else if (this.props.toggle) {
			return (
				<button className="button" onClick={this.handleClick}>
					{this.props.name} <i className="icon icon-arrow-down"></i>
				</button>
			);
		} else {
			return (
				<button className="button" onClick={this.handleClick}>
					{this.props.name} <i className="icon icon-arrow-up"></i>
				</button>
			);
		}
	}
}

class ButtonHelp extends Component {
	constructor(props) {
		super(props);

		this.state = {
			showModal: false,
		};
	}

	handleClick = () => {
		console.log('HELLO!', this.state.showModal);

		this.setState(state => ({
			showModal: !this.state.showModal,
		}));
	};

	render() {
		return (
			<span>
				<button className="button help" onClick={this.handleClick}>
					<img src={help} alt="help" />
				</button>
				<div
					className={
						'modal ' + (this.state.showModal ? 'active' : '')
					}
				>
					<a
						href="#close"
						className="modal-overlay"
						aria-label="Close"
						onClick={this.handleClick}
					></a>
					<div className="modal-container">
						<div className="modal-header">
							<a
								href="#close"
								className="btn btn-clear float-right"
								aria-label="Close"
								onClick={this.handleClick}
							></a>
							<div className="modal-title h5">Help</div>
						</div>
						<div className="modal-body">
							<div className="content columns">
								<div className="column col-6">
									<b>Usage</b>
									<p>
										Memes can be saved by using button{' '}
										<kbd>add</kbd>, <kbd>ctrl+v</kbd> or{' '}
										<kbd>drag&drop</kbd>.
									</p>
									<b>Edit</b>
									<p>
										Click on place which you want to edit
										(there is possibility to change:{' '}
										<i>title</i>, <i>description</i>,{' '}
										<i>image url</i>).
									</p>
								</div>
								<div className="column col-6">
									<b>Commands</b>
									<ul>
										<li>
											<mark>/demo</mark> to restore
											default memes for presentation
											purpose
										</li>
										<li>
											<mark>/clear</mark> to remove all
											memes from your local history
										</li>
									</ul>
									<i>(write commands in search area)</i>
								</div>
							</div>
						</div>
						<div className="modal-footer">Maciej A. Czyzewski</div>
					</div>
				</div>
			</span>
		);
	}
}

class Column extends Component {
	constructor(props) {
		super(props);

		var value = this.props.data[this.props.idx][this.props.name];

		this.state = {
			isToggleOn: true,
			value: value,
			isDefault: value === 'Description' || value === 'Title',
		};
	}

	handleClick = () => {
		if (this.state.isToggleOn === true) {
			this.setState(state => ({
				isToggleOn: false,
			}));
		}
	};

	onInputChange(value) {
		this.props.data[this.props.idx][this.props.name] = value;
		this.setState(state => ({
			value: value,
			isDefault: value === 'Description' || value === 'Title',
		}));
	}

	onBlur = () => {
		this.setState({
			isToggleOn: true,
		});
	};

	modifier() {
		return <p>{this.state.value}</p>;
	}

	render() {
		if (this.state.isToggleOn) {
			return (
				<div
					className={
						'column ' +
						this.props.bonusClass +
						' ' +
						(this.state.isDefault ? 'bg-warning' : '')
					}
					onClick={this.handleClick}
				>
					{this.modifier()}
				</div>
			);
		} else {
			return (
				<div
					className={
						'column ' +
						this.props.bonusClass +
						' ' +
						(this.state.isDefault ? 'bg-warning' : '')
					}
					onClick={this.handleClick}
				>
					<input
						ref={input => input && input.focus()}
						onChange={e => this.onInputChange(e.target.value)}
						onBlur={this.onBlur}
						type="text"
						className="button form-input"
						value={this.state.value}
					/>
				</div>
			);
		}
	}
}

class ColumnTitle extends Column {
	modifier() {
		return <h1>{this.state.value}</h1>;
	}
}

class ColumnImage extends Column {
	modifier() {
		return <img className="meme" src={this.state.value} alt="" />;
	}
}

class Star extends Component {
	handleClick = () => {
		console.log('CLICK', this.props.rate);
		this.props.parent.handleClick(this.props.rate);
	};
	handleHover = () => {
		console.log('HOVER', this.props.rate);
		this.props.parent.handleHover(this.props.rate);
	};
	handleOut = () => {
		console.log('OUT', this.props.rate);
		this.props.parent.handleOut(this.props.rate);
	};

	render() {
		return (
			<img
				src={this.props.type}
				className="star"
				alt="star"
				onClick={this.handleClick}
				onMouseOver={this.handleHover}
				onMouseOut={this.handleOut}
			/>
		);
	}
}

class ColumnRating extends Column {
	constructor(props) {
		super(props);

		var value = this.props.data[this.props.idx][this.props.name];

		this.state = {
			isToggleOn: true,
			value: value,
			isDefault: value === '?',
			fakeValue: value,
		};
	}

	generate(rate) {
		var rows = [];
		var i;
		for (i = 1; i <= rate; i++) {
			rows.push(<Star key={i} rate={i} type={star_full} parent={this} />);
		}
		for (i = 1; i <= 5 - rate; i++) {
			rows.push(
				<Star
					key={rate + i}
					rate={rate + i}
					type={star_empty}
					parent={this}
				/>,
			);
		}
		return rows;
	}

	handleClick = rate => {
		console.log('PARENT CLICK', rate);
		if (isFinite(String(rate))) {
			this.setState({ value: rate });
			this.props.data[this.props.idx]['rating'] = rate;
		}
	};
	handleHover = rate => {
		console.log('PARENT HOVER', rate);
		this.setState({ fakeValue: rate });
	};
	handleOut = rate => {
		console.log('PARENT OUT', rate, this.state.value);
		this.setState({ fakeValue: this.state.value });
	};

	modifier() {
		return (
			<div className="stars-view">
				{this.generate(this.state.fakeValue)}
				<small>{this.state.value}</small>
			</div>
		);
	}
}

class ColumnAction extends Component {
	render() {
		return (
			<div className="column">
				<Button name="delete" handle={this.props.handle} />
			</div>
		);
	}
}

////////////////////////////////////////////////////////////////////////////////

class Item extends Component {
	constructor(props) {
		super(props);
		console.log(this.props.parent);
	}

	handleClick = () => {
		console.log('DELETE this is:', this);
		this.props.parent.delete(this.props.data[this.props.idx]['idx']);
	};

	render() {
		return (
			<div
				className={
					'row columns col-gapless ' +
					(this.props.data[this.props.idx]['opacity'] === 0
						? 'bg-shadow'
						: '')
				}
			>
				<ColumnImage
					idx={this.props.idx}
					name="image"
					data={this.props.data}
					bonusClass="meme"
				/>{' '}
				<div className="column info">
					<ColumnTitle
						idx={this.props.idx}
						name="name"
						data={this.props.data}
					/>{' '}
					<Column
						idx={this.props.idx}
						name="desc"
						data={this.props.data}
					/>{' '}
					<ColumnRating
						idx={this.props.idx}
						name="rating"
						data={this.props.data}
					/>{' '}
					<ColumnAction handle={this.handleClick} />
				</div>
			</div>
		);
	}
}

////////////////////////////////////////////////////////////////////////////////

class App extends Component {
	constructor(props) {
		super(props);

		var data = [];
		var search = '';
		var local_data = null;
		var local_search = null;

		try {
			local_data = JSON.parse(localStorage.getItem('data'));
			local_search = localStorage.getItem('search');
		} catch (error) {
			console.log('ERROR', error);
		}

		if (local_data !== null) {
			data = local_data;
		} else {
			data = DEMO_DATA;
		}

		if (local_search !== null) {
			search = local_search;
		}

		this.state = {
			data: data,
			isToggleOn: true,
			inputValue: search,
		};
	}

	componentDidMount() {
		console.log('STARTING');
		var intervalId = setInterval(this.checkpoint.bind(this), 3000);
		this.setState({ intervalId: intervalId });
	}

	componentWillUnmount() {
		clearInterval(this.state.intervalId);
	}

	generate() {
		var rows = [];
		for (var i = 0; i < this.state.data.length; i++) {
			rows.push(
				<Item
					idx={i}
					key={this.state.data[i]['name'] + this.state.data[i]['idx']}
					data={this.state.data}
					parent={this}
				/>,
			);
		}
		return rows;
	}

	checkpoint() {
		console.log('SAVING FOR LATER!');
		// FIXME: remove opacity TAG!
		console.log('DEBUG', this.state.data);
		localStorage.setItem('search', this.state.inputValue);
		localStorage.setItem('data', JSON.stringify(this.state.data));
	}

	handleDragOver = e => {
		let event = e;
		event.stopPropagation();
		event.preventDefault();
		console.log('OMG WE HAVE IT-->', event);
		var imageUrl = event.dataTransfer.getData('text/html');
		if (imageUrl !== '') {
			console.log('FIND!!!');
			var rex = /src="?([^"\s]+)"?\s*/;
			var url = rex.exec(imageUrl);
			console.log(imageUrl);
			url[1] = url[1].replace(/&amp;/g, '&');
			console.log('----->', url[1]);
			this.new(url[1]);
		}
	};

	handlePaste = e => {
		var url = e.clipboardData.getData('Text');
		if (validURL(url)) {
			this.new(url);
		}
	};

	new(url) {
		console.log('new player!');
		var array = this.state.data;
		var randomIdx = Math.random();
		var img_url = `https://picsum.photos/400/300/?random=${randomIdx}`;
		if (validURL(url)) img_url = url;
		array.unshift({
			idx: randomIdx,
			name: 'Title',
			desc: 'Description',
			image: img_url,
			rating: 0,
			opacity: 1,
		});
		this.setState({ data: array });
	}

	delete(idx) {
		console.log('PARENT DELETE', idx);
		var array = this.state.data;
		var ids = array.map(function (obj) {
			return obj.idx;
		});
		var index = ids.indexOf(idx);
		console.log('YEAY', array);
		delete array[index];
		array = array.filter(Boolean);
		console.log('YEAY', array);
		this.setState({ data: array });
	}

	// FIXME: if clear, welcome message

	search() {
		var text = this.state.inputValue;
		console.log('SEARHC', text);
		var array = [];
		var array_end = [];
		for (var i = 0; i < this.state.data.length; i++) {
			var record = this.state.data[i];
			if (
				record['name'].includes(text) ||
				record['desc'].includes(text)
			) {
				record['opacity'] = 1;
				array.push(record);
			} else {
				record['opacity'] = 0;
				array_end.push(record);
			}
		}
		if (text === '/clear') {
			console.log('CLEAR');
			localStorage.clear();
			this.setState({ data: [] });
		} else if (text === '/demo') {
			console.log('DEMO');
			this.setState({ data: DEMO_DATA });
		} else {
			console.log('SEARHC2', text);
			this.setState({ data: array.concat(array_end) });
		}
	}

	sort() {
		console.log('SORT');
		var array = this.state.data;

		this.setState(state => ({
			isToggleOn: !state.isToggleOn,
		}));

		array.sort(function (a, b) {
			return a['rating'] - b['rating'];
		});

		if (this.state.isToggleOn) {
			array = array.reverse();
		}

		this.setState({ data: array });
	}

	updateInputValue(e) {
		console.log();
		this.setState({ inputValue: e }, () => {
			this.search();
		});
	}

	render() {
		return (
			<div
				className="App container"
				onDragOver={this.handleDragOver}
				onDrop={this.handleDragOver}
				onPaste={this.handlePaste}
			>
				<img
					className="show-xl logo-small"
					src={doge}
					alt="doge territory"
				/>
				<hr className="separator" />
				<div className="columns">
					<div className="logo hide-xl column col-4">
						<h2>
							<img src={doge} alt="doge territory" /> Meme
							Professor
						</h2>
					</div>
					<div className="column col-xl-6 col-4">
						<Button name="add" handle={this.new.bind(this)} />{' '}
						<Button
							name="sort by rating"
							handle={this.sort.bind(this)}
							toggle={this.state.isToggleOn}
						/>{' '}
						<ButtonHelp />
					</div>
					<div className="column col-xl-6 col-4">
						<input
							type="text"
							onChange={e =>
								this.updateInputValue(e.target.value)
							}
							value={this.state.inputValue}
							className="button form-input"
							placeholder="write here to search"
						/>
					</div>
				</div>
				<hr className="separator" />
				{this.generate()}
			</div>
		);
	}
}

export default App;
