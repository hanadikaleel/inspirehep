import { connect } from 'react-redux';

import Highlights from '../components/Highlights';
import { addHighlightedRecords } from '../../actions/literature';

const stateToProps = (state) => ({
  disabled: state.authors.get('publicationSelection').size === 0,
});

const dispatchToProps = (dispatch) => ({
  onAssign({ from, to }) {
    dispatch(addHighlightedRecords({ from, to }));
  },
});

export default connect(stateToProps, dispatchToProps)(Highlights);
